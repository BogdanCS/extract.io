from malletconverter import MalletConverter
import globals
import calendar

class DocumentInformation(object):
    def __init__(self, paper, prepro, index):
        self.uiText = MalletConverter.getRawDataAsString(globals.PUBMED_ABSTRACT_FIELD_NAME, paper)
        self.title = MalletConverter.getField(globals.PUBMED_TITLE_FIELD_NAME, paper) 
        self.text   = MalletConverter.preprocess(prepro, self.uiText)
        
        self.topicList = []

        dateStr = MalletConverter.getField(globals.PUBMED_PUBLISH_YEAR_FIELD_NAME, paper)
        month =  MalletConverter.getField(globals.PUBMED_PUBLISH_MONTH_FIELD_NAME, paper)
        if len(month) == 1:
            month = '0' + month
        if not month.isdigit():
            month = list(calendar.month_abbr).index(month_abbr)

        dateStr += "-" + month
        print dateStr
        # Named year for "legacy" reasons
        self.year   = dateStr 
        self.labels = MalletConverter.getLabels(globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        # Used for mapping LLDA results to the input document
        self.index = index
