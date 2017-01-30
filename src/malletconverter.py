class MalletConverter:
    # Transform XML into a Mallet corpus
    @staticmethod
    def xmlToMallet(xmlData, prepro, idField, dataField):
        output = ""
        for index in range(len(xmlData)):
            try:
                line = ""
                #line += MalletConverter.__find(idField, xmlData[index]).next()
                line += MalletConverter.getDocId(idField, xmlData[index])
                line += " en "
                #line += MalletConverter.__preprocess(prepro, MalletConverter.__find(dataField, xmlData[index]).next())
                line += MalletConverter.getDataAsString(dataField, prepro, xmlData[index])
                line += "\n"

                output += line
            except StopIteration:
                print "Abstract not found"
        return output
        
    # Preprocess the document and transform it in a string
    @staticmethod
    def getDataAsString(dataField, prepro, doc):
        return MalletConverter.__preprocess(prepro, MalletConverter.__find(dataField, doc).next())

    @staticmethod
    def getDocId(idField, doc):
        return MalletConverter.__find(idField, doc).next()

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
