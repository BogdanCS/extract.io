from malletconverter import MalletConverter
from globals import Globals

class DocumentInformation(object):
    def __init__(self, paper, prepro, index):
        self.text   = MalletConverter.getDataAsString(Globals.PUBMED_ABSTRACT_FIELD_NAME, prepro, paper)
        # !! NORMALISE YEARS BASED ON TOTAL DOCS / YEAR
        self.year   = MalletConverter.getField(Globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        self.labels = MalletConverter.getLabels(Globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        self.index = index
        
