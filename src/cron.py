import json
import io
import hunspell
import logging

#from nltk.stem import *

from globals import Globals
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from preprocesser import PostPreprocesser
from malletconverter import MalletConverter
from documentclusterer import TopTopicClusterer
from topicmodel import LLDATopicModel
from topicmodel import LDATopicModel

import webapp2

class Cron(webapp2.RequestHandler):
    
    def get(self):
        logging.info("Cron starting..")
        pubmed = PubmedRetriever()
        #todo update
        NO_DOCS = 15
        papers = pubmed.getDocumentsIf("diabetes", NO_DOCS)

        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        postpre = PostPreprocesser()
        (malletCorpus, labels) = MalletConverter.xmlToMallet(papers, prepro, postpre,
                                                             Globals.PUBMED_ID_FIELD_NAME, 
                                                             Globals.PUBMED_ABSTRACT_FIELD_NAME,
                                                             Globals.PUBMED_LABELS_FIELD_NAME)

        # Store corpus and labels
        logging.info("Start writing to file")
        with io.FileIO(Globals.CORPUS_PATH, "w") as file:
            file.write(malletCorpus.encode('utf8'))
        with io.FileIO(Globals.CORPUS_LABELS_PATH, "w") as file:
            file.write(json.dumps(labels))

        logging.info("Stop writing to file")
        
        # Train Labelled LDA model
        LLDATopicModel().trainModel(malletCorpus, labels)

        # Train unsupervised LDA model
        LDATopicModel().trainModel() #malletCorpus

        # group abstract per topic
        #for i in range(0,10):
        #    print model.get_document_topics(mm[i])
        #gensim.corpora.mmcorpus.MmCorpus.serialize('corpus_training.mm', corpus)
        #mm = gensim.corpora.mmcorpus.MmCorpus('corpus_training.mm') # `mm` document stream now has random access
        # either get abbreviatons from first occurence in text or get it from some web service

# TODO : Have different routes for different training sets
application = webapp2.WSGIApplication([('/cron', Cron)], debug=True)

if __name__ == "__main__":
    #run_wsgi_app(application)
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
