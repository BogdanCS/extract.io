import logging
import gensim

from abc import ABCMeta, abstractmethod   

from globals import Globals
import labellda


class TopicModel:
    __metaclass__ = ABCMeta

    @abstractmethod
    def trainModel(self, corpus, labels) : pass
    def loadModel(self, identifier) : pass
    # Gets text document return list of tuples (topicId, probability)
    def getTopicComposition(self, doc) : pass
    def getTopicTopWords(self, topicId) : pass

class LLDATopicModel(TopicModel):
    def trainModel(self, malletCorpus, labels):
        logging.info("Train supervised LDA")
    
        # malletCorpus is a string formatted in mallet style, indexed by PMID
        # labels dictionary where key is PMID and value is a string of space
        # separated labels
        (train_space, train_labels) = self.__unpack(malletCorpus, labels)
        print train_space
        print train_labels

        stmt = labellda.STMT(Globals.LLDA_MODEL_NAME, epochs=400, mem=14000)
        stmt.train(train_space, train_labels)
        
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
        return (tuple(train_space), tuple(train_labels))
    
class LDATopicModel(TopicModel):
    def __init__(self):
        self.bowConverter = gensim.corpora.Dictionary()
        try:
            _ = self.bowConverter.merge_with(Globals.CORPUS.id2word) 
        except:
            logging.warn("No corpus found")
        
    def trainModel(self, corpus=None, labels=None): # get Mallet corpus from file
        logging.info("Train unsupervised LDA")
        corpus = gensim.corpora.MalletCorpus(Globals.CORPUS_PATH)
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=8, num_topics=75, iterations=500)
        model.save(Globals.TRAINED_MODEL_PATH)

    def getTopicComposition(self, docText):
        bow = self.bowConverter.doc2bow(docText.split())
