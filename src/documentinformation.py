from malletconverter import MalletConverter
import globals

class DocumentInformation(object):
    def __init__(self, paper, prepro, index):
        pmid = MalletConverter.getField(globals.PUBMED_ID_FIELD_NAME, paper) 
        rawText = MalletConverter.getRawDataAsString(globals.PUBMED_ABSTRACT_FIELD_NAME, paper)
        title = MalletConverter.getField(globals.PUBMED_TITLE_FIELD_NAME, paper) 
        self.uiText = "PMID:" + pmid + "<br>" + title + "<br><br>" + rawText
        self.text   = MalletConverter.preprocess(prepro, rawText)
        
        # !! NORMALISE YEARS BASED ON TOTAL DOCS / YEAR
        self.year   = MalletConverter.getField(globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        self.labels = MalletConverter.getLabels(globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        self.index = index
        
