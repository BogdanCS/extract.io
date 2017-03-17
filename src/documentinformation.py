from malletconverter import MalletConverter
from operator import itemgetter
import globals
import calendar
import math

# POINTWISE MUTUAL INFORMATION TOPIC CO OCCURENCE

from decimal import *

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
           # Swallow exception
            try:
                month = list(calendar.month_abbr).index(month_abbr)
            except:
                month = '01'

        dateStr += "-" + month
        # Named year for "legacy" reasons
        self.year   = dateStr 
        self.labels = MalletConverter.getLabels(globals.PUBMED_LABELS_FIELD_NAME, paper)
        
        # NOTE: This the index within the Python Dictionary not PMID
        # Used for mapping LLDA results to the input document
        self.index = index
        
        # Keep this for extracting summary
        self.prepro = prepro
        self.summaries = {}

    def getWordProb(self, word, wordsProb):
        word = word.rstrip()
        prob = [probT for wordT, probT in wordsProb if wordT == word]

        if len(prob) == 0 or prob[0] == 0.0:
            prob = 1.0
        else:
            prob = prob[0]
        return prob
        
    def setSummaries(self, topics):
        words = self.uiText.split()
        wordsLength = len(words)
        for topicId in self.topicList:
            topic = topics[topicId]
            bestScore = 0.0
            windowStart = 0
            windowEnd = 14
            scoreSoFar = [0.0] * wordsLength
            countGoodWords = [0] * wordsLength
            for idx in range(windowStart, windowEnd + 1):
                if idx > 0:
                    countGoodWords[idx] = countGoodWords[idx-1]
                word = words[idx]
                preproWord = self.prepro.stemWords(
                             self.prepro.removePunctuation(
                             self.prepro.removeCapitals(word)))
                prob = self.getWordProb(preproWord, topic.wordsProb)
                if prob != 1.0:
                    countGoodWords[idx] = countGoodWords[idx]+1
                if idx > 0:
                    scoreSoFar[idx] = scoreSoFar[idx-1] * prob 
                else:
                    scoreSoFar[idx] = prob
            bestScore = scoreSoFar[windowEnd] * countGoodWords[windowEnd]
            self.summaries[topic.uid] = (windowStart, windowEnd)

            windowStart = windowStart + 1
            windowEnd = windowEnd + 1
            while (windowEnd < wordsLength):
                countGoodWords[windowEnd] = countGoodWords[windowEnd-1]
                word = words[windowEnd]
                preproWord = self.prepro.stemWords(
                             self.prepro.removePunctuation(
                             self.prepro.removeCapitals(word)))
                probNewWord = self.getWordProb(preproWord, topic.wordsProb)
                if probNewWord != 1.0:
                    countGoodWords[windowEnd] = countGoodWords[windowEnd] + 1
                scoreSoFar[windowEnd] = scoreSoFar[windowEnd-1] * probNewWord
                probNewWind = scoreSoFar[windowEnd]/scoreSoFar[windowStart-1]*(countGoodWords[windowEnd]-countGoodWords[windowStart-1])
                if(probNewWind > bestScore):
                    bestScore = probNewWind
                    self.summaries[topic.uid] = (windowStart, windowEnd)
                windowStart = windowStart + 1
                windowEnd = windowEnd + 1
            #Debugging
            print self.uiText.encode('utf8')
            print topic.nameTokens
            print topic.wordsProb
            (start, end) = self.summaries[topic.uid]
            for wordsIdx in range(start, end+1):
                print words[wordsIdx].encode('utf8') + " ",
            print "END!!!"
            print
        del self.prepro

    def getWordProbDec(self, word, wordsProb, wordProbAvg, title, maxProb):
        # There is a left over space at the end of both word and title tokens
        if word in title:
            return Decimal(maxProb + 1)

        word = word.rstrip()
        prob = [probT for wordT, probT in wordsProb if wordT == word]

        if len(prob) == 0 or prob[0] == 0.0:
            prob = Decimal(0.0000001)
        else:
            prob = Decimal(prob[0])/wordProbAvg[word]
        return prob
        
    def __getMaxProb(self, wordsProb):
        return max(wordsProb, key=itemgetter(1))[1]
        
    def setSummariesDec(self, topics, wordProbAvg):
        words = self.uiText.split()

        wordsLength = len(words)
        windowSize = int(math.floor(wordsLength * 0.07))
        #getcontext().prec = 100
        for topicId in self.topicList:
            topic = topics[topicId]
            maxProb = self.__getMaxProb(topic.wordsProb)
            title = [self.prepro.stemWords(self.prepro.removeCapitals(token)) for token in topic.nameTokens]
            bestScore = 0.0
            windowStart = 0
            windowEnd = max(windowSize, 10) #14
            scoreSoFar = [Decimal(0)] * wordsLength
            for idx in range(windowStart, windowEnd + 1):
                word = words[idx]

                preproWord = self.prepro.stemWords(
                             self.prepro.removePunctuation(
                             self.prepro.removeCapitals(word)))
                prob = self.getWordProbDec(preproWord, topic.wordsProb, wordProbAvg, title, maxProb)
                if idx > 0:
                    # Addition?
                    scoreSoFar[idx] = scoreSoFar[idx-1] + prob 
                else:
                    scoreSoFar[idx] = prob
            bestScore = scoreSoFar[windowEnd]
            self.summaries[topic.uid] = (windowStart, windowEnd)

            windowStart = windowStart + 1
            windowEnd = windowEnd + 1
            while (windowEnd < wordsLength):
                word = words[windowEnd]
                preproWord = self.prepro.stemWords(
                             self.prepro.removePunctuation(
                             self.prepro.removeCapitals(word)))
                probNewWord = self.getWordProbDec(preproWord, topic.wordsProb, wordProbAvg, title, maxProb)
                scoreSoFar[windowEnd] = scoreSoFar[windowEnd-1] + probNewWord
                probNewWind = scoreSoFar[windowEnd]-scoreSoFar[windowStart-1]
                if(probNewWind > bestScore):
                    bestScore = probNewWind
                    self.summaries[topic.uid] = (windowStart, windowEnd)
                windowStart = windowStart + 1
                windowEnd = windowEnd + 1
            #Debugging
            print self.uiText.encode('utf8')
            print topic.nameTokens
            print topic.wordsProb
            (start, end) = self.summaries[topic.uid]
            for wordsIdx in range(start, end+1):
                print words[wordsIdx].encode('utf8') + " ",
            print "END!!!"
            print
        del self.prepro
