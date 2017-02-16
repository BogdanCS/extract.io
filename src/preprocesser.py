from abc import ABCMeta, abstractmethod   
from nltk.corpus import stopwords
import os
import logging
import time
import nltk
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'lib', 'nltk', 'nltk_data'))

from string import punctuation
import regex as re

# This component deals with
# - text cleansing
# - tokenizing
# - stemming (morphological analysis)

# TODO
# - do not remove upper case if whole word is upper case? (-> abbreviation)
# - concatanate abstracts together?
# - special handling of ' ?
# - research how to deal with numbers/quantities. erase only quantities
# - initial acronym detection and expansion - post TA?
# - chunking pre/post TA?
# - unify different forms (e.g NP4 APL and NP4-APL) pre/post TA?

# Basically, I don't two different tokens with the same meaning e.g Patient, patient, patients
# DI and diabetes or DI and insipidus have different meanings

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

    # We should split on punctuation and add the heuristics
    # as in Documents lab
    def removePunctuation(self, string):
        regex = re.compile('[^a-zA-Z0-9- ]+')
        return regex.sub('', string)

    def removeCapitals(self, string):
        result = ""
        for word in string.split():
            if word.isupper():
                result += word + " "
            else:
                result += word.lower() + " "
        return result

class PostPreprocesser:
    # Filter out words that appear in more than 60% of the documents
    # And in less than 5%
    # Also filter out lone numbers and one letter words
    def postPreprocess(self, text, wordOccCount, noDocs):
        logging.info("Start filtering/postprocessing")
        start = time.time()
        
        output = ""
        for line in text.splitlines():
            components = line.split(None, 2)
            if (len(components) <= 2):
                # Drop line, no text
                continue
            
            # Copy back to the string what does not need to be filtered
            output += components[0] + ' ' + components[1] + ' ';
            for word in components[2].split():
                if(word.isdigit() or len(word)==1 or self.__isExtreme(word, wordOccCount, noDocs)):
                    continue
                output += word + ' ';
                
            # Replace last space with new line
            # get rid of this
            output = output[:-1]
            output += '\n'
            
        end = time.time()
        logging.info("Stop filtering. Time(sec): ")
        logging.info(end-start)
        
        return output
        
    def __isExtreme(self, word, wordOccurenceCounter, noDocs):
        noOcc = wordOccurenceCounter[word]
        return noOcc > noDocs * 0.75 or noOcc < noDocs * 0.05
        
    
#class TerMinePreprocesser(Preprocesser):
    #def concatanateTexts(textList):

#    def oneSentencePerLine(text):
        #TODO point might not mean end of sentence
#        return text.replace('.', '\n')
            
