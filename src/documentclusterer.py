from abc import ABCMeta, abstractmethod   
from operator import itemgetter

from globals import Globals

#class DocumentClusterer:
#    __metaclass__ = ABCMeta
#
#    @abstractmethod
#    # Returns pairs of cluster index - list of indexes of original documents
#    def getClusters(self, bowList, modelFeatures) : pass
    

class TopTopicClusterer:

    def getDocClusters(self, doc_bow, modelFeatures, clusters):
        for docId, docData in doc_bow.iteritems():
            topicDistrib = modelFeatures.get_document_topics(docData)
            maxIdx = self.__getMaxTopicIndex(topicDistrib)
            if (maxIdx not in clusters):
                raise Exception('Topic id not found')
            # Append document to the corresponding cluster identified by topic id
            clusters[maxIdx].docs.append(Globals.PUBMED_SEARCH_URL + str(docId))
        return clusters
        
    def __getMaxTopicIndex(self, topicDistrib):
        return max(topicDistrib, key=itemgetter(1))[0]
            

# class KMeansClusterer: