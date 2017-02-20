import logging
import hunspell
import datetime

import globals 
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter
from documentinformation import DocumentInformation

class DocumentManager():

    def getDocuments(self, req):
        logging.info("getDocuments()")
        
        req['startDate'] = self.__epochToString(req['startDate'])
        req['endDate'] = self.__epochToString(req['endDate'])
        logging.info("Looking for documents between " + req['startDate']
                     + " and " + req['endDate'])

        pubmed = PubmedRetriever()
        # TODO - Add the timestamps
        # Retrieve abstracts
        papers = pubmed.getDocumentsIf(req['keywords'], req['limit'], 
                                       req['startDate'], req['endDate'])

        # Create preprocesser
        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        
        # Recreate Document ID - DocumentInformation mapping
        globals.PROCESSED_CACHED_CORPUS = {}
        index = 0
        for paper in papers:
            # Swallow exceptions due to invalid data
            try:
                docUID = MalletConverter.getField(globals.PUBMED_ID_FIELD_NAME, paper)
                globals.PROCESSED_CACHED_CORPUS[docUID] = DocumentInformation(paper, prepro, index)
                # Don't count docs without abstracts
                index = index + 1
            except StopIteration:
                logging.warn("Abstract not found")

    def __epochToString(self, ms):
        print ms
        date = datetime.datetime.fromtimestamp(float(ms))
        return str(date.year) + "/" + str(date.month) + "/"+ str(date.day)
