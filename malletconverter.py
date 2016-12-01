from nltk.corpus import stopwords
from string import punctuation
import regex as re

class MalletConverter:
    @staticmethod
    def toMallet(xmlData, idField, dataField):
        output = ""
        for index in range(len(xmlData)):
            try:
                line = ""
                line += MalletConverter.__find(idField, xmlData[index]).next()
                line += " en "
                line += MalletConverter.__preprocess(MalletConverter.__find(dataField, xmlData[index]).next())
                line += "\n"

                output += line
            except StopIteration:
                print "Abstract not found"
        return output

    @staticmethod
    def __find(key, doc):
        if hasattr(doc, 'iteritems'):
            for k, v in doc.iteritems():
                if k == key:
                    if isinstance(v, list):
                        yield ''.join(v)
                    else:
                        yield v
                if isinstance(v, dict):
                    for result in MalletConverter.__find(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in MalletConverter.__find(key, d):
                            yield result

    @staticmethod
    def __preprocess(line):
        # Remove capital case
        procLine = line.lower()
        # Remove punctuation
        re.sub(ur"\p{P}+", "", procLine)
        # Remove stopwords
        filterLine = ""
        for word in procLine.split(): 
            if word not in stopwords.words('english'):
                filterLine += word + " "
        return filterLine
