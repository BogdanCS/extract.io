import logging
import time
import gensim
import io
import json
import re
import numpy as np 
import sklearn.metrics as skm 

from abc import ABCMeta, abstractmethod   
from operator import itemgetter

import globals
import labellda

from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser

# Adapter for the underlying topic models
class TopicModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def trainModel(self, corpus=None, labels=None) : pass
    # Input text for which topic composition must be computed
    # Return list of tuples (topicId, probability)
    def getTopicComposition(self, text) : pass
    # Returns a list of tokens(words) which are part of the name
    def getTopicName(self, topicId) : pass
    # Returns a list of tuples (word, probability)
    def getTopicWords(self, topicId) : pass

class LLDATopicModel(TopicModel):
    # - Pass a previously trained LLDA model
    #   or create an empty model and train it later by calling trainModel
    #   If the model has been passed, also pass the label names for each 
    #   label in the training set
    # - Pass a test dataset for inference
    #   or pass it later using inferTopics
    def __init__(self, model=None, testDataset=None):
        self.model = model

        self.results = None
        self.trueLabels = None
        # Mapping between label name and words associated with label
        # The indices correspond with the columns in results and trueLabels
        self.words = None
        
        if self.model and testDataset:
            self.inferTopics(testDataset)
            
    def trainModel(self, malletCorpus, labels):
        logging.info("Train supervised LDA")
    
        if malletCorpus == None or labels == None:
            raise Exception("Parameters required for LLDA not provided")
            
        # malletCorpus is a string formatted in mallet style, indexed by PMID
        # labels dictionary where key is PMID and value is a string of space
        # separated labels
        (train_space, train_labels) = self.__unpackMallet(malletCorpus, labels)
        print train_space
        print train_labels

        stmt = labellda.STMT(globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        stmt.train(train_space, train_labels)
        
        # Load the newly trained model and update cache
        model = labellda.STMT(globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        globals.LLDA_MODEL = model
        
    def inferTopics(self, dataset):
        if not self.model:
            raise Exception("Model has not been trained")

        (test_space, test_labels) = self.__unpackDocInfo(dataset)
        self.model.test(test_space, test_labels)
        
        (self.trueLabels, self.results, self.words) = self.model.results(test_labels, array=True)

    def getTopicComposition(self, docInfo):
        output = []
        
        if self.results is None:
            raise Exception("No test set has been provided")
            
        docResults = self.results[docInfo.index]
        # Convert to list of tuples
        for index, prob in enumerate(docResults):
            output.append((index, prob))
            
        # Filter out unlikely labels
        # Need to normalise topic proabilities with the other models
        output = [(index, prob) for (index, prob) in output if prob > globals.TOPIC_PROB_THRESHOLD]
        return output
            
    def __unpackDocInfo(self, dataset):
        train_space = []
        train_labels = []
        for docUID, docInfo in dataset.iteritems():
            train_space.append(docInfo.text)
            train_labels.append(docInfo.labels)
        return (tuple(train_space), tuple(train_labels))
            
    def __unpackMallet(self, malletCorpus, labels):
        train_space = []
        train_labels = []
        for line in malletCorpus.splitlines():
            components = line.split(None, 2)
            train_space.append(components[2])
            train_labels.append(labels[components[0]])
        return (tuple(train_space), tuple(train_labels))
        
    def getTopicWords(self, topicId):
        return self.words[topicId][1]
        
    def getTopicName(self, topicId):
        # We are storing multi word label names as camel case - convert back to original version
        tokens = re.findall('[0-9a-zA-Z][^A-Z-]*', self.words[topicId][0])
        return tokens
        
    def getPerplexity(self):
        # A try to calculate perplexity in the same way as gensim
        # there is a python implementation of LLDA that has perplexity
        # better try to replicate that
        return np.exp(skm.log_loss(self.trueLabels, self.results))
        
    def getAvgPrecisions(self):
        return skm.average_precision_score(self.trueLabels, self.results)
    #def getAccuracy(self):
    # get recall
    # get text ...
    # skm ftw

class LDATopicModel(TopicModel):
    # Pass a previously trained LDA model
    # or create an empty model and train it later by calling
    # trainModel
    def __init__(self, model=None):
        self.model = model
        self.bowConverter = gensim.corpora.Dictionary()
        if model:
            _ = self.bowConverter.merge_with(globals.CORPUS.id2word) 
        # Flush?
        self.bowCache = []
        
    def trainModel(self, corpus=None, labels=None): # get Mallet corpus from file
        logging.info("Train unsupervised LDA")
        corpus = gensim.corpora.MalletCorpus(globals.CORPUS_PATH)
        _ = self.bowConverter.merge_with(globals.CORPUS.id2word) 
        self.model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=8, num_topics=75, iterations=500)
        self.model.save(globals.TRAINED_MODEL_PATH)
        
        # Update cache
        LDA_MODEL = self.model

    def getTopicComposition(self, docInfo):
        bow = self.bowConverter.doc2bow(docInfo.text.split())
        self.bowCache.append(bow)
        # globals.THRESHOLD ?
        return self.model.get_document_topics(bow)

    def getTopicWords(self, topicId):
        #return self.model.show_topic(topicId, topn=len(self.model.id2word))
        return self.model.show_topic(topicId, topn=globals.WORDS_PER_TOPIC)
        
    # For unsupervised LDA we don't have a name (i.e label) for topics
    # We will try to assign a MeSH label to the topic based on top 10 words
    ### We return the top 5 words associated with the topic
    def getTopicName(self, topicId):
        output = []

        topWords = self.model.show_topic(topicId, topn=10)
        
        pubmed = PubmedRetriever()
        query = ""
        for word, prob in topWords:
            query += word + " OR "
        query = query[:-4]
        candidateLabels = pubmed.getDocumentsIf(query, 10, None, None, "mesh")
        
        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') 
        prepro = PubmedPreprocesser(stemmer)
        for label, text in candidateLabels.iteritems():
            text = prepro.stemWords(
                   prepro.removeStopWords(
                   prepro.removePunctuation(
                   prepro.removeCapitals(text))))
        
        return output
        
    def getPerplexity(self):
        logging.info("Start getPerplexity")
        start = time.time()
        
        perplexity = np.exp2(-self.model.log_perplexity(self.bowCache))
        
        end = time.time()
        logging.info("Stop preprocessing. Time(sec): ")
        logging.info(end-start)
        
        return perplexity
        
