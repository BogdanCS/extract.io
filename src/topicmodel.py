import logging
import gensim
import io
import json
import re

from abc import ABCMeta, abstractmethod   
from operator import itemgetter

import globals
import labellda

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
    def __init__(self, model=None, uniqTrainLabels=None, testDataset=None):
        self.model = model
        self.uniqTrainLabels = uniqTrainLabels

        self.results = None
        self.trueLabels = None
        # The ith element in any row from results/trueLabels
        # corresponds to labelNames[i]
        self.labelNames = None
        
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
        
        # Here we are replicating TMT behaviour
        # Consider moving this to a common library
        # Store individual unique labels for later use
        self.uniqTrainLabels = []
        seenLabels = set()
        for labelString in train_labels:
            for label in labelString.split():
                if label not in seenLabels:
                    self.uniqTrainLabels.append(label)
                    seenLabels.add(label)
                    
        # TODO: Use file written by TMT
        with io.FileIO(globals.CORPUS_LABELS_IDX_PATH, "w") as file:
            file.write(json.dumps(self.uniqTrainLabels))

        # Load the newly trained model and update cache
        model = labellda.STMT(globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        globals.LLDA_MODEL = model
        
    def inferTopics(self, dataset):
        if not self.model:
            raise Exception("Model has not been trained")

        (test_space, test_labels) = self.__unpackDocInfo(dataset)
        self.model.test(test_space, test_labels)
        
        (self.trueLabels, self.results) = self.model.results(test_labels, array=True)
        self.labelNames = self.__getLabelsNames(test_labels)

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
        return [("", 0.0)]
        
    def getTopicName(self, topicId):
        # We are storing multi word label names as camel case - convert back to original version
        tokens = re.findall('[0-9a-zA-Z][^A-Z-]*', self.labelNames[topicId])
        return tokens

    # Filter out training labels that are not in the test dataset
    def __getLabelsNames(self, testLabels):
        labelSet = set()
        for labelString in testLabels:
            for label in labelString.split():
                labelSet.add(label)
                
        return [label for label in self.uniqTrainLabels if label in labelSet]
    
class LDATopicModel(TopicModel):
    # Pass a previously trained LDA model
    # or create an empty model and train it later by calling
    # trainModel
    def __init__(self, model=None):
        self.model = model
        self.bowConverter = gensim.corpora.Dictionary()
        if model:
            _ = self.bowConverter.merge_with(globals.CORPUS.id2word) 
        
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
        # globals.THRESHOLD ?
        return self.model.get_document_topics(bow)

    def getTopicWords(self, topicId):
        return self.model.show_topic(topicId, topn=len(self.model.id2word))
        
    # For unsupervised LDA we don't have a name (i.e label) for topics
    # We return the top 5 words associated with the topic
    def getTopicName(self, topicId):
        output = []

        topWords = self.model.show_topic(topicId, topn=5)
        for word, prob in topWords:
            output.append(word)

        return output
        
