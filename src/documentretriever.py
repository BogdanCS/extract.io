from abc import ABCMeta, abstractmethod   
from Bio import Entrez
from time import sleep
from random import randint
from string import ascii_letters

import globals

# Abstract super class for the Retriever classes
class DocumentRetriever:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getDocumentsIf(query, maxNumber) : pass
    

# Concrete Retriever class for Pubmed/Medline
class PubmedRetriever(DocumentRetriever):

    def getDocumentsIf(self, query, maxNumber, startDate, endDate, dbName='pubmed'):
        results = self.__search(query, maxNumber, startDate, endDate, dbName)
        id_list = results['IdList']
        papers = self.__fetch_details(id_list, dbName)
        
        return papers #?['PubmedArticle'] ?# Standard Python dictionary format

    def __search(self, query, maxNumber, startDate, endDate, dbName):
        Entrez.email = 'bogdan.stoian11@gmail.com'
        handle = None
        if (dbName == 'pubmed'):
            handle = Entrez.esearch(db=dbName, 
                                    sort='relevance', 
                                    retmax=maxNumber,
                                    retmode='xml', 
                                    datetype='pdat',
                                    mindate=startDate,
                                    maxdate=endDate,
                                    #retstart=randint(0,3000), # to test this with min date, max date
                                    term=query)
        elif (dbName == 'mesh'):
            handle = Entrez.esearch(db=dbName, 
                                    sort='relevance', 
                                    retmax=maxNumber,
                                    retmode='xml', 
                                    term=query)
            
        results = Entrez.read(handle)
        return results

    def __getMeshLabel(self, line):
        nonLetter = ''.join(set(map(chr, range(128))) - set(ascii_letters))
        line = line.lstrip(nonLetter)
        line = line.rstrip()
        return (" ".join(reversed(line.split(",")))).lstrip()
        
    def __fetch_details(self, id_list, dbName):
        results = []

        # Split the id list into evenly sized chunks
        id_list = [id_list[i:i + globals.PUBMED_FETCH_LIMIT] for i in xrange(0, len(id_list), globals.PUBMED_FETCH_LIMIT)]

        Entrez.email = 'bogdan.stoian11@gmail.com'
        for chunk in id_list:
            chunk = ','.join(chunk)
            handle = Entrez.efetch(db=dbName,
                                   retmode='xml',
                                   id=chunk)
            # MeSH database queries do not support XML
            if(dbName == 'mesh'):
                lines = handle.readlines()
                
                labelName = ""
                text = ""
                # Do some preliminary preprocessing
                for line in lines:
                    if line[0].isdigit() and line[1] == ":":
                        # Drop subheadings
                        idx = labelName.find('[')
                        if (idx == -1):
                            results.append((labelName,text))

                        labelName = self.__getMeshLabel(line)
                        text = ""
                    else:
                        text += " ".join(line.split()) + " "    

                results = results[1:]
            else:
                records = Entrez.read(handle)
                results.extend(records['PubmedArticle'])
        return results
