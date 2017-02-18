from globals import Globals

class DocumentManager():

    def getDocuments(self, req):
        logging.info("getDocuments()")
        
        pubmed = PubmedRetriever()
        # TODO - Add the timestamps
        # Retrieve abstracts
        print req['startDate']
        print req['endDate']
        papers = pubmed.getDocumentsIf(req['keywords'], req['limit'], 
                                       req['startDate'], req['endDate'])

        # Create preprocesser
        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        
        # Recreate Document ID - DocumentInformation mapping
        Globals.PROCESSED_CACHED_CORPUS = {}
        for index, paper in enumerate(papers):
            # Swallow exceptions due to invalid data
            try:
                docUID = MalletConverter.getField(Globals.PUBMED_ID_FIELD_NAME, paper)
                Globals.PROCESSED_CACHED_CORPUS[docUID] = DocumentInformation(paper, prepro, index)
            except StopIteration:
                logging.warn("Abstract not found")