import logging
import time
import random
import hunspell
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
        # Document blacklist
        self.blacklist = None
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

        stmt = labellda.STMT(globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        stmt.train(train_space, train_labels)
        
        # Load the newly trained model and update cache
        model = labellda.STMT(globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        # For evaluation purposes load up all the words per topic
        self.words = model.getWords()
        globals.LLDA_MODEL = model
        
    def inferTopics(self, dataset):
        if not self.model:
            raise Exception("Model has not been trained")

        (test_space, test_labels) = self.__unpackDocInfo(dataset)
        self.model.test(test_space, test_labels)
        
        (self.trueLabels, self.results, self.words, self.blacklist) = self.model.results(test_labels, array=True)

    def getTopicComposition(self, docInfo):
        output = []
        
        if self.results is None:
            raise Exception("No test set has been provided")
            
        if (docInfo.index in self.blacklist):
            logging.warn("Ignore blacklisted document")
            return output

        docResults = self.results[docInfo.index]
        # Convert to list of tuples
        for index, prob in enumerate(docResults):
            output.append((index, prob))
            
        # Filter out unlikely labels
        # Need to normalise topic proabilities with the other models
        output = [(index, prob) for (index, prob) in output if prob > globals.TOPIC_PROB_THRESHOLD * 0.010]
        print "LLDA topics %d" % len(output)
        return output
            
    def __unpackDocInfo(self, dataset):
        train_space = []
        train_labels = []
        for docUID, docInfo in sorted(dataset.iteritems(), key=lambda (k,v): v.index):
            train_space.append(docInfo.text)
            train_labels.append(docInfo.labels)
        train_space
        return (tuple(train_space), tuple(train_labels))
            
    def __unpackMallet(self, malletCorpus, labels):
        train_space = []
        train_labels = []
        for line in malletCorpus.splitlines():
            components = line.split(None, 2)
            train_space.append(components[2])
            train_labels.append(labels[components[0]])
        return (tuple(train_space), tuple(train_labels))
        
    def getAllTopics(self):
        observCohText = ""
        intrudWorText = ""
        intrudWorList = ""
        
        for jdx, value in enumerate(self.words):
            wordsProb = value[1]
            intrudId = random.randint(0, len(wordsProb))
            intrudWord = self.generateIntruder(jdx)
            for idx, (word, prob) in enumerate(wordsProb):
                observCohText += word + " "
                if idx == intrudId:
                    intrudWorText += intrudWord + " "
                    intrudWorList += intrudWord + "\n"
                intrudWorText += word + " "
            observCohText += "\n"
            intrudWorText += "\n"
        return (observCohText, intrudWorText, intrudWorList)
        
    def generateIntruder(self, jdx):
        iterations = 10
        idx = random.randint(0, len(self.words) - 1)
        while (idx == jdx and iterations > 0):
            idx = random.randint(0, len(self.words) - 1)
            iterations = iterations - 1
            
        iterations = 10
        print self.words[idx]
        kdx = random.randint(0, len(self.words[idx][1]) - 1)
        while (self.words[idx][1][kdx] in self.words[jdx][1] and iterations > 0):
            kdx = random.randint(0, len(self.words[idx][1]) - 1)
            iterations = iterations - 1
            
        return self.words[idx][1][kdx][0]
        
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
        
    def getAvgPrecision(self):
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
        
        self.topicIdToName = {}
        self.tp = 0
        self.fp = 0

        # word - (avg prob, max prob)
        self.wordAverageMax = {}
        
        self.bowConverter = gensim.corpora.Dictionary()
        if model:
            _ = self.bowConverter.merge_with(globals.CORPUS.id2word) 
        # Flush?
        self.bowCache = []
        
    def trainModel(self, corpus=None, labels=None): # get Mallet corpus from file
        logging.info("Train unsupervised LDA")
        corpus = gensim.corpora.MalletCorpus(globals.CORPUS_PATH)
        _ = self.bowConverter.merge_with(globals.CORPUS.id2word) 
        self.model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=7, num_topics=75, iterations=300)
        self.model.save(globals.TRAINED_MODEL_PATH)
        
        # Update cache
        LDA_MODEL = self.model

    # SET MINIMUM PROBABILITY FOR BOTH LDA AND LLDA !!!

    def getTopicComposition(self, docInfo):
        bow = self.bowConverter.doc2bow(docInfo.text.split())
        self.bowCache.append(bow)
        # globals.THRESHOLD ?
        topics = self.model.get_document_topics(bow, minimum_probability=globals.TOPIC_PROB_THRESHOLD)
        # Assign labels on demand
        print docInfo.labels
        for topicId, prob in topics:
            label = self.assignLabel(topicId)
            label = "".join(label.split())
            if len(label) == 0:
                logging.warn("No label assigned")
                continue
            elif label in docInfo.labels:
                self.tp = self.tp + 1
            else:
                self.fp = self.fp + 1

        logging.info("LDA topics %d" % len(topics))
        return topics

    def getTopicWords(self, topicId):
        #return self.model.show_topic(topicId, topn=len(self.model.id2word))
        return self.model.show_topic(topicId, topn=globals.WORDS_PER_TOPIC)
        
    def computeOverlap(self, label, text , topWords):
        overlap = 0.0
        
        for word in label.split():
            if word.lower() in topWords:
                overlap += self.wordAverageMax[word.lower()][1]/self.wordAverageMax[word.lower()][0] 
        for word in text.split():
            if word in topWords:
                overlap += topWords[word]/self.wordAverageMax[word][0]
        return overlap
        
    def assignLabel(self, topicId):
        if topicId in self.topicIdToName:
            return " ".join(self.topicIdToName[topicId])

        topWords = dict(self.model.show_topic(topicId, topn=5))
        self.updateWordAverage(topWords)
        #trueTopWords = self.getTrueTopWords(topWords)
        print "COMPARE"
        print topWords
        #print trueTopWords

        pubmed = PubmedRetriever()
        query = ""
        for word in topWords.iterkeys():
            query += word + " OR "
        query = query[:-4]
        candidateLabels = pubmed.getDocumentsIf(query, 10, None, None, "mesh")
        
        candidateLabels = [(label, self.__preprocess(text)) for (label, text) in candidateLabels]
        
        bestLabel = ""
        bestOverlap = 0.0
        for (label, text) in candidateLabels:
            overlap = self.computeOverlap(label, text, topWords)
            if overlap > bestOverlap:
                bestOverlap = overlap
                bestLabel = label
                
        self.topicIdToName[topicId] = bestLabel.split()
        return bestLabel
        
    def updateWordAverage(self, topWords):
        for word in topWords.keys():
            if word not in self.wordAverageMax:
                likelyTopics = self.model.get_term_topics(self.bowConverter.token2id[word])
                print "GUARD"
                print likelyTopics
                if len(likelyTopics) == 0:
                    logging.info("Word not found")
                    self.wordAverageMax[word] = (0.0, 0.0)
                else:
                    self.wordAverageMax[word] = (float(sum([pair[0] for pair in likelyTopics]))/float(len(likelyTopics)),
                                                 max(likelyTopics, key=itemgetter(1))[1])
        
    def getTrueTopWords(self, topWords):
        trueTopWords = []
        for word in topWords.keys():
            if word not in self.wordAverageMax:
                likelyTopics = self.model.get_term_topics(self.bowConverter.token2id[word])
                print "GUARD"
                print likelyTopics
                if len(likelyTopics) == 0:
                    logging.info("Word not found")
                    self.wordAverageMax[word] = (0.0, 0.0)
                else:
                    self.wordAverageMax[word] = (float(sum([pair[0] for pair in likelyTopics]))/float(len(likelyTopics)),
                                                 max(likelyTopics, key=itemgetter(1))[1])
            trueTopWords.append((word, float(topWords[word])/float(self.wordAverageMax[word][0])))
        trueTopWords = sorted(trueTopWords, key=itemgetter(1))
        #trueTopWords = [word for word,prob in trueTopWords]
        trueTopWords = trueTopWords[:5]
        return dict(trueTopWords)
        
    # For unsupervised LDA we don't have a name (i.e label) for topics
    # We will try to assign a MeSH label to the topic based on top 10 words
    # Lesk algorithm
    ### We return the top 5 words associated with the topic
    def getTopicName(self, topicId):
        topWords = dict(self.model.show_topic(topicId, topn=5))
        tokens = topWords.keys()
        #tokens = self.getTrueTopWords(topWords).keys()
        tokens.append('  (')
        tokens.extend(self.topicIdToName[topicId])
        tokens[-1] = tokens[-1] + "* )"
        return tokens
        
    def getAvgPrecision(self):
        return float(self.tp)/float(self.tp+self.fp)
        
    def getPerplexity(self):
        logging.info("Start getPerplexity")
        start = time.time()
        
        perplexity = np.exp2(-self.model.log_perplexity(self.bowCache))
        
        end = time.time()
        logging.info("Stop getPerplexity. Time(sec): ")
        logging.info(end-start)
        
        return perplexity
        
    def getAllTopics(self):
        topics = self.model.show_topics(num_topics=-1, formatted=False)
        observCohText = ""
        intrudWorText = ""
        intrudWorList = ""
        for topicId, topicWords in topics:
            intrudId = random.randint(0, len(topicWords) - 1)
            intrudWord = self.generateIntruder(topicId, len(topics), topicWords)
            for idx, (word,prob) in enumerate(topicWords):
                observCohText += word + " "
                if idx == intrudId:
                    intrudWorText += intrudWord + " "
                    intrudWorList += intrudWord + "\n"
                intrudWorText += word + " "
            observCohText += "\n"
            intrudWorText += "\n"
        return (observCohText, intrudWorText, intrudWorList)

    def generateIntruder(self, jdx, noTopics, jdxWords):
        iterations = 10
        idx = random.randint(0, noTopics - 1)
        while (idx == jdx and iterations > 0):
            idx = random.randint(0, noTopics - 1)
            iterations = iterations - 1
        words = self.model.show_topic(idx, topn=15)
        
        iterations = 10
        kdx = random.randint(0, len(words) - 1)
        while (words[kdx][1] in jdxWords and iterations > 0):
            kdx = random.randint(0, len(words) - 1)
            iterations = iterations - 1
            
        return words[kdx][0]
        
    def __preprocess(self, line):
        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') 
        prepro = PubmedPreprocesser(stemmer)
        return prepro.stemWords(
               prepro.removeStopWords(
               prepro.removePunctuation(
                      line.lower())))
        
