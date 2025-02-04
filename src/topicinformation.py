#class TopicBasicInfo(object):
#    def __init__(self, idx):
#        self.idx = idx
#        self.words = []
#
#    # We could have done this in the constructor but
#    # we want the TopicBasicInfo construction to be cheap
#    # since we are sometimes using it only as a wrapper for the idx
#    def getTopicWords(self, model):
#        topWords = model.show_topic(self.idx, topn=5)
#        for word, prob in topWords:
#            self.words.append(word)
#            
#    def __hash__(self):
#        return hash((self.idx))
#        
#    def __eq__(self, other):
#        return self.idx == other.idx
#
#    def __ne__(self, other):
#        return not self.__eq__(other)

from operator import itemgetter

from sortedcontainers import SortedList
from sortedcontainers import SortedListWithKey
import math

class TopicInformation(object):
    def __init__(self, uid, nameTokens, wordsProb):
        self.uid = uid
        self.nameTokens = nameTokens
        
        # Inverted index
        self.docs = SortedListWithKey(key=itemgetter(1))
        
        # The years when the documents stored in self.docs have been published
        # Keep duplicate values so we can create a histogram for temporal trends / topic
        self.years = {}
        self.forecastYears = {}
        # Top year for topic - including forecasted years
        self.maxYearCount = 0

        self.score = 0
        
        # Words associated with topic and their probability
        # list of tuples
        self.wordsProb = wordsProb
        
    # No longer need for the SortedList
    # Convert to regular list
    def finaliseYears(self):
        self.years = self.__finaliseYears(self.years)
        self.forecastYears = self.__finaliseYears(self.forecastYears, False)
        print self.forecastYears
        
    def __finaliseYears(self, years, month=True):
        expandedYears = []
        for yearMonth, count in years.iteritems():
            year = yearMonth
            if month:
                year = yearMonth.split('-')[0]
            if count > self.maxYearCount:
                self.maxYearCount = count
            for i in range(0, count):
                expandedYears.append(year)
        expandedYears.sort()
        return expandedYears
        
    # No longer need for the SortedList
    # Convert to regular list
    # Sorted by this topic relevance in doc
    def finaliseDocs(self):
        self.docs = [d for (d, p) in reversed(self.docs)]

    
