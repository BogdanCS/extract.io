import gensim
import io
import hunspell
import logging

#from nltk.stem import *

from globals import Globals
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter
from documentclusterer import TopTopicClusterer

import webapp2

class Cron(webapp2.RequestHandler):
    
    def get(self):
        logging.info("Cron starting..")
        pubmed = PubmedRetriever()
        #todo update
        papers = pubmed.getDocumentsIf("diabetes", 10000)

        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        malletCorpus = MalletConverter.xmlToMallet(papers, prepro, 
                                                   Globals.PUBMED_ID_FIELD_NAME, 
                                                   Globals.PUBMED_ABSTRACT_FIELD_NAME)

        # database ?
        with io.FileIO(Globals.CORPUS_PATH, "w") as file:
            file.write(malletCorpus.encode('utf8'))

        corpus = gensim.corpora.MalletCorpus(Globals.CORPUS_PATH)
        model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', passes=20, num_topics=100, iterations=500)
        model.save(Globals.TRAINED_MODEL_PATH)

        # either get abbreviatons from first occurence in text or get it from some web service

        # group abstract per topic
        #for i in range(0,10):
        #    print model.get_document_topics(mm[i])
        gensim.corpora.mmcorpus.MmCorpus.serialize('corpus_training.mm', corpus)
        mm = gensim.corpora.mmcorpus.MmCorpus('corpus_training.mm') # `mm` document stream now has random access

        print model.show_topic(0)
        print model.show_topics(num_topics=5, num_words=5)
        

# TODO : Have different routes for different training sets
application = webapp2.WSGIApplication([('/cron', Cron)], debug=True)

if __name__ == "__main__":
    #run_wsgi_app(application)
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
