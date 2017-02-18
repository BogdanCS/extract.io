import logging
import gensim

from abc import ABCMeta, abstractmethod   
from operator import itemgetter

from globals import Globals
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

class LLDATopicModel(TopicModel):
    # - Pass a previously trained LLDA model
    #   or create an empty model and train it later by calling trainModel
    #   If the model has been passed, also pass the label names for each 
    #   label in the training set
    # - Pass a test dataset for inference
    #   or pass it later using inferLabels
    def __init__(self, model=None, trainLabels=None, dataset=None):
        self.model = model
        self.trainLabels = trainLabels

        self.results = None
        self.trueLabels = None
        # The ith element in any row from results/trueLabels
        # corresponds to labelNames[i]
        self.labelNames = None
        
        if self.model and dataset:
            inferLabels(dataset)
            
    def trainModel(self, malletCorpus, labels):
        logging.info("Train supervised LDA")
    
        if malletCorpus == None or labels == None:
            raise Exception("Parameters required for LLDA not provided")
            
        # malletCorpus is a string formatted in mallet style, indexed by PMID
        # labels dictionary where key is PMID and value is a string of space
        # separated labels
        (train_space, train_labels) = self.__unpack(malletCorpus, labels)
        print train_space
        print train_labels

        stmt = labellda.STMT(Globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        stmt.train(train_space, train_labels)
        
        # Store individual unique labels for later use
        self.trainLabels = []
        seenLabels = set()
        for labelString in train_labels:
            for label in labelString.split():
                if label not in seenLabels:
                    self.trainLabels.append(label)
                    seenLabels.add(label)
                    
        # write to file ??

        # Load the newly trained model and update cache
        model = labellda.STMT(Globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        Globals.LLDA_MODEL = model
        
    def inferLabels(self, dataset):
        if not self.model:
            raise Exception("Model has not been trained")

        (test_space, test_labels) = _unpack(dataset)
        self.model.test(test_space, test_labels)
        
        (self.trueLabels, self.results) = self.model.results(test_labels, array=True)
        self.labelNames = __getLabelNames(test_labels)

    def getTopicComposition(docInfo):
        output = []
        
        if not results:
            raise Exception("No test set has been provided")
            
        docResults = results[docInfo.index]
        # Convert to list of tuples
        for index, prob in enumerate(docResults):
            output.append(tuple(index, prob))
            
        # Filter out unlikely labels
        # Need to normalise topic proabilities with the other models
        output = [(index, prob) for (index, prob) in output if prob > Globals.TOPIC_PROB_THRESHOLD]
        return output
            
    # need to normalise this for both training and testing use
    def __unpack(self, malletCorpus, labels):
        train_space = []
        train_labels = []
        for line in malletCorpus.splitlines():
            components = line.split(None, 2)
            train_space.append(components[2])
            print components[0]
            print labels[components[0]]
            train_labels.append(labels[components[0]])
        print len(train_space)
        print len(train_labels)
        self.__saveUniqueLabelIdx(train_labels)
        return (tuple(train_space), tuple(train_labels))
        
    def getTopicName(self, topicId):
        return self.labelNames[topicId]

    def __getLabelsNames(self, testLabels):
        labelSet = set()
        for labelString in testLabels:
            for label in labelString.split():
                labelSet.add(label)
                
        return [label for label in trainLabels if label in labelSet]
    
class LDATopicModel(TopicModel):
    # Pass a previously trained LDA model
    # or create an empty model and train it later by calling
    # trainModel
    def __init__(self, model=None):
        self.model = model
        self.bowConverter = gensim.corpora.Dictionary()
        if model:
            _ = self.bowConverter.merge_with(Globals.CORPUS.id2word) 
        
    def trainModel(self, corpus=None, labels=None): # get Mallet corpus from file
        logging.info("Train unsupervised LDA")
        corpus = gensim.corpora.MalletCorpus(Globals.CORPUS_PATH)
        _ = self.bowConverter.merge_with(Globals.CORPUS.id2word) 
        self.model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=8, num_topics=75, iterations=500)
        self.model.save(Globals.TRAINED_MODEL_PATH)
        
        # Update cache
        LDA_MODEL = self.model

    def getTopicComposition(self, docInfo):
        bow = self.bowConverter.doc2bow(docInfo.text.split())
        return self.model.get_document_topics(bow)

    # For unsupervised LDA we don't have a name (i.e label) for topics
    # We return the top 5 words associated with the topic
    def getTopicName(self, topicId):
        output = []

        topWords = self.model.show_topic(topicId, topn=5)
        for word, prob in topWords:
            output.append(word)

        return output
        
