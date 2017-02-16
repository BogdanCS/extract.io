import logging
import gensim

from globals import Globals
import labellda

class LLDATopicModel:
    def trainModel(self, malletCorpus, labels):
        logging.info("Train supervised LDA")
    
        # malletCorpus is a string formatted in mallet style, indexed by PMID
        # labels dictionary where key is PMID and value is a string of space
        # separated labels
        (train_space, train_labels) = self.__unpack(malletCorpus, labels)
        print train_space
        print train_labels

        stmt = labellda.STMT('labellda_model', epochs=400, mem=14000)
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
    
            

class LDATopicModel:
    def trainModel(self): # get Mallet corpus from file
        logging.info("Train unsupervised LDA")
        corpus = gensim.corpora.MalletCorpus(Globals.CORPUS_PATH)
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=8, num_topics=75, iterations=500)
        model.save(Globals.TRAINED_MODEL_PATH)
