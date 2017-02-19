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

    def getDocClusters(self, docId, docInfo, model, clusters):
        #for docId, docInfo in docs.iteritems():
        topicComposition = model.getTopicComposition(docInfo)
        maxIdx = self.__getMaxTopicIndex(topicComposition)
        if (maxIdx not in clusters):
            raise Exception('Topic id not found')
        # Append document to the corresponding cluster identified by topic id
        clusters[maxIdx].docs.append(Globals.PUBMED_SEARCH_URL + str(docId))
        # Add its year of publishment
        clusters[maxIdx].years.add(docInfo.year)
        
    def __getMaxTopicIndex(self, topicComposition):
        return max(topicComposition, key=itemgetter(1))[0]
            

# class KMeansClusterer:
