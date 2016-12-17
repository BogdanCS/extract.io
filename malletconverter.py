class MalletConverter:
    @staticmethod
    def toMallet(xmlData, prepro, idField, dataField):
        output = ""
        for index in range(len(xmlData)):
            try:
                line = ""
                line += MalletConverter.__find(idField, xmlData[index]).next()
                line += " en "
                line += MalletConverter.__preprocess(prepro, MalletConverter.__find(dataField, xmlData[index]).next())
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

    #make it easy to adapt this
    #e.g easy to change between different stemmers
    @staticmethod
    def __preprocess(prepro, line):
        print line.encode('utf8')
        return prepro.stemWords(
               prepro.removeStopWords(
               prepro.removePunctuation(
               prepro.removeCapitals(line))))

        # Remove capital case
        #line = line.lower()
        # Remove all non alphabetic chars
        # re.sub(ur"\p{P}+", "", procLine)
        #regex = re.compile('[^a-zA-Z ]')
        #line = regex.sub('', line)
        # Remove stopwords and stem
        #filterLine = ""
        #stemmer = SnowballStemmer("english")
        #for word in line.split(): 
        #    if word not in stopwords.words('english'):
        #        filterLine += stemmer.stem(word) + " "
        #return filterLine
