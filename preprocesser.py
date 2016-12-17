from abc import ABCMeta, abstractmethod   
from nltk.corpus import stopwords
from string import punctuation
import regex as re

# This component deals with
# - text cleansing
# - tokenizing
# - stemming (morphological analysis)

# TODO
# - initial acronym detection and expansion
# - research how to deal with numbers/quantities. erase only quantities?
# - chunking pre/pos TA?
# - unify different forms (e.g NP4 APL and NP4-APL) pre/pos TA?
class Preprocesser:
    __metaclass__ = ABCMeta

    @abstractmethod
    def stemWords(string) : pass
    def removeStopWords(string) : pass
    def removePunctuation(string) : pass
    def removeCapitalCase(string) : pass


class PubmedPreprocesser(Preprocesser):
    def __init__(self, stemmer):
        self.stemmer = stemmer

    def stemWords(self, string):
        result = ""
        for word in string.split():
            stemWord = self.stemmer.stem(word)
            if (isinstance(stemWord, basestring)):
                result += stemWord + " "
            elif (isinstance(stemWord, list) and stemWord):
                result += stemWord[0] + " "
            else:
                result += word + " "
        return result
    
    def removeStopWords(self, string):
        result = ""
        for word in string.split():
            if word not in stopwords.words('english'):
                result += word + " "
        return result

    def removePunctuation(self, string):
        regex = re.compile('[^a-zA-Z0-9- ]+')
        return regex.sub('', string)

    def removeCapitals(self, string):
        return string.lower()
