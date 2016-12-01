from abc import ABCMeta, abstractmethod   
from Bio import Entrez

# Abstract super class for the Retriever classes
class DocumentRetriever:
    __metaclass__ = ABCMeta

    @abstractmethod
    def getDocumentsIf(query, maxNumber) : pass
    

# Concrete Retriever class for Pubmed/Medline
class PubmedRetriever(DocumentRetriever):

    def getDocumentsIf(self, query, maxNumber):
        results = self.__search(query, maxNumber)
        id_list = results['IdList']
        papers = self.__fetch_details(id_list)
        
        return papers # Standard Python dictionary format

    def __search(self, query, maxNumber):
        Entrez.email = 'bogdan.stoian11@gmail.com'
        handle = Entrez.esearch(db='pubmed', 
                                sort='relevance', 
                                retmax=maxNumber,
                                retmode='xml', 
                                term=query)
        results = Entrez.read(handle)
        return results

    def __fetch_details(self, id_list):
        ids = ','.join(id_list)
        Entrez.email = 'bogdan.stoian11@gmail.com'
        handle = Entrez.efetch(db='pubmed',
                            retmode='xml',
                            id=ids)
        results = Entrez.read(handle)
        return results
