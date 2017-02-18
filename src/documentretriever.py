from abc import ABCMeta, abstractmethod   
from Bio import Entrez
from time import sleep
from globals import Globals
from random import randint

# Abstract super class for the Retriever classes
class DocumentRetriever:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getDocumentsIf(query, maxNumber) : pass
    

# Concrete Retriever class for Pubmed/Medline
class PubmedRetriever(DocumentRetriever):

    def getDocumentsIf(self, query, maxNumber, startDate, endDate):
        results = self.__search(query, maxNumber, startDate, endDate)
        id_list = results['IdList']
        papers = self.__fetch_details(id_list)
        
        return papers #?['PubmedArticle'] ?# Standard Python dictionary format

    def __search(self, query, maxNumber, startDate, endDate):
        Entrez.email = 'bogdan.stoian11@gmail.com'
        handle = Entrez.esearch(db='pubmed', 
                                sort='relevance', 
                                retmax=maxNumber,
                                retmode='xml', 
                                datetype='pdat',
                                mindate=startDate,
                                maxdate=endDate,
                                #retstart=randint(0,3000), # to test this with min date, max date
                                term=query)
        results = Entrez.read(handle)
        return results

    def __fetch_details(self, id_list):
        results = []

        # Split the id list into evenly sized chunks
        id_list = [id_list[i:i + Globals.PUBMED_FETCH_LIMIT] for i in xrange(0, len(id_list), Globals.PUBMED_FETCH_LIMIT)]

        Entrez.email = 'bogdan.stoian11@gmail.com'
        for chunk in id_list:
            chunk = ','.join(chunk)
            handle = Entrez.efetch(db='pubmed',
                                   retmode='xml',
                                   id=chunk)
            records = Entrez.read(handle)
            results.extend(records['PubmedArticle'])
        return results
