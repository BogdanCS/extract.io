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
                if word == "gene":
                    self.getWordProb(preproWord, topic.wordsProb)
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
                
        del self.prepro
