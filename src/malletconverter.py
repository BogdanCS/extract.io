import logging
import time

class MalletConverter:
    # Transform XML into a Mallet corpus
    @staticmethod
    # TODO: Move out the filtering
    def xmlToMallet(xmlData, prepro, postpre, idField, dataField, labelField):
        output = ""
        wordOccurenceCounter = {}
        labels = {}

        noDocs = len(xmlData)
        logging.info("Start preprocessing")
        start = time.time()
        for index in range(noDocs):
            try:
                wordSetPerDoc = set()

                line = ""
                pmid = MalletConverter.getField(idField, xmlData[index])
                
                labels[pmid] = MalletConverter.getLabels(labelField, xmlData[index])
                line += pmid + " en "
                
                # This returns a text which has already been preprocessed
                print dataField
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
        
        return (postpre.postPreprocess(output, wordOccurenceCounter, noDocs),
                labels)
        
    # Preprocess the document and transform it in a string
    # TODO : Refactor this component and move out the following functions?
    @staticmethod
    def getLabels(labelField, doc):
        output = ""
        meshHeadings = MalletConverter.__find(labelField, doc).next()
        if len(meshHeadings)==0:
            # TODO: Need to handle this - i.e take document out of the corpus
            logging.error("No headings found")

        for heading in meshHeadings:
            processedHeading = "".join(reversed(heading["DescriptorName"].split(",")))
            processedHeading = "".join(processedHeading.split())
            output += processedHeading + " "
            
        output = output[:-1]
        return output 

    @staticmethod
    def getDataAsString(dataField, prepro, doc):
        data = MalletConverter.__find(dataField, doc).next()
        if isinstance(data, list) and len(data) == 0:
            raise StopIteration("Abstract not found")
        elif isinstance(data, list):
            data = data[0]

        return MalletConverter.__preprocess(prepro, data)

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
                        if(len(v) > 0 and isinstance(v[0], str)):
                            yield ''.join(v)
                        else:
                            yield v
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
        return prepro.stemWords(
               prepro.removeStopWords(
               prepro.removePunctuation(
               prepro.removeCapitals(line))))
