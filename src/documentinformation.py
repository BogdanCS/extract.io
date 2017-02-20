from malletconverter import MalletConverter
import globals

class DocumentInformation(object):
    def __init__(self, paper, prepro, index):
        self.text   = MalletConverter.getDataAsString(globals.PUBMED_ABSTRACT_FIELD_NAME, prepro, paper)
        # !! NORMALISE YEARS BASED ON TOTAL DOCS / YEAR
        self.year   = MalletConverter.getField(globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        self.labels = MalletConverter.getLabels(globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        self.index = index
        
