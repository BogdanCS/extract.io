from malletconverter import MalletConverter

class DocumentInformation(object):
    def __init__(self, paper, prepro):
        self.text   = MalletConverter.getDataAsString(Globals.PUBMED_ABSTRACT_FIELD_NAME, prepro, paper)
        # !! NORMALISE YEARS BASED ON TOTAL DOCS / YEAR
        self.year   = MalletConverter.getField(Globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        self.labels = MalletConverter.getLabels(Globals.PUBMED_LABELS_FIELD_NAME, paper)
        
