from malletconverter import MalletConverter
import globals

class DocumentInformation(object):
    def __init__(self, paper, prepro, index):
        #pmid = MalletConverter.getField(globals.PUBMED_ID_FIELD_NAME, paper) 
        self.uiText = MalletConverter.getRawDataAsString(globals.PUBMED_ABSTRACT_FIELD_NAME, paper)
        self.title = MalletConverter.getField(globals.PUBMED_TITLE_FIELD_NAME, paper) 
        #self.uiText = "PMID:" + pmid + "<br>" + title + "<br><br>" + rawText
        self.text   = MalletConverter.preprocess(prepro, self.uiText)
        
        self.topicList = []

        # !! NORMALISE YEARS BASED ON TOTAL DOCS / YEAR
        self.year   = MalletConverter.getField(globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        self.labels = MalletConverter.getLabels(globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        # Used for mapping LLDA results to the input document
        self.index = index
