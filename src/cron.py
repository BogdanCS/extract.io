import json
import io
import hunspell
import logging

#from nltk.stem import *

import globals
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
        papers = pubmed.getDocumentsIf("diabetes", NO_DOCS, "2006", "2016")

        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        postpre = PostPreprocesser()
        (malletCorpus, labels) = MalletConverter.xmlToMallet(papers, prepro, postpre,
                                                             globals.PUBMED_ID_FIELD_NAME, 
                                                             globals.PUBMED_ABSTRACT_FIELD_NAME,
                                                             globals.PUBMED_LABELS_FIELD_NAME)

        # Store corpus and labels
        logging.info("Start writing to file")
        with io.FileIO(globals.CORPUS_PATH, "w") as file:
            file.write(malletCorpus.encode('utf8'))
        with io.FileIO(globals.CORPUS_LABELS_PATH, "w") as file:
            file.write(json.dumps(labels))

        logging.info("Stop writing to file")
        
        # Train Labelled LDA model
        LLDATopicModel().trainModel(malletCorpus, labels)

        # Train unsupervised LDA model
        LDATopicModel().trainModel() #malletCorpus

# TODO : Have different routes for different training sets
application = webapp2.WSGIApplication([('/cron', Cron)], debug=True)

if __name__ == "__main__":
    #run_wsgi_app(application)
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
