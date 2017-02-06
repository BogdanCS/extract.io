import logging
import time

class MalletConverter:
    # Transform XML into a Mallet corpus
    @staticmethod
    # TODO: Move out the filtering
    def xmlToMallet(xmlData, prepro, idField, dataField):
        output = ""
        wordOccurenceCounter = {}

        noDocs = len(xmlData)
        logging.info("Start preprocessing")
        start = time.time()
        for index in range(noDocs):
            try:
                wordSetPerDoc = set()

                line = ""
                line += MalletConverter.getField(idField, xmlData[index])
                line += " en "
                
                # This returns a text which has already been preprocessed
                text = MalletConverter.getDataAsString(dataField, prepro, xmlData[index])
                
                # Update our occurence counter used for filtering extremes
                for word in text.split(' '):
                    if word not in wordSetPerDoc:
                        wordSetPerDoc.add(word)
                        if word not in wordOccurenceCounter:
                            wordOccurenceCounter[word] = 1
                        else:
                            wordOccurenceCounter[word] = wordOccurenceCounter[word] + 1;
                            
                line += text
                line += "\n"

                output += line
            except StopIteration:
                logging.info("Abstract not found")
                
        end = time.time()
        logging.info("Stop preprocessing. Time(sec): ")
        logging.info(end-start)
        
        logging.info("Start filtering")
        start = time.time()
        # Filter out words that appear in more than 60% of the documents
        # And in less than 5%
        # Also filter out lone numbers and one letter words - this is a bit of a hack - should move to preprocesser
        # This is very slow -> should be made linear multiple passes
        # one to erase lines that are empty
        # move word above/under threshold to a set
        for word, noOccurences in wordOccurenceCounter.iteritems():
            if (noOccurences > noDocs * 0.75 or noOccurences < noDocs * 0.05
                or word.isdigit() or len(word)==1) and word != "en":
                #The string has been pre processed, can only be surounded by whitespace
                output = output.replace(" " + word + " ", " ")
            
        end = time.time()
        logging.info("Stop filtering. Time(sec): ")
        logging.info(end-start)
        
        return output
        
    # Preprocess the document and transform it in a string
    # TODO : Refactor this component and move out the following functions?
    @staticmethod
    def getDataAsString(dataField, prepro, doc):
        return MalletConverter.__preprocess(prepro, MalletConverter.__find(dataField, doc).next())

    @staticmethod
    def getField(field, doc):
        if(field == "PMID"):
            return doc["MedlineCitation"]["PMID"]
        return MalletConverter.__find(field, doc).next()
        
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

    #TODO - create abreviation - long form mapping from what is available in text
    @staticmethod
    def __preprocess(prepro, line):
        #print line.encode('utf8')
        return prepro.stemWords(
               prepro.removeStopWords(
               prepro.removePunctuation(
               prepro.removeCapitals(line))))
