from abc import ABCMeta, abstractmethod   
from operator import itemgetter

import globals
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
        if len(topicComposition) == 0:
            logging.warn("No topics inferred")
            return

        #maxIdx = self.__getMaxTopicIndex(topicComposition)
        #if (maxIdx not in clusters):
        #    raise Exception('Topic id not found')
        topicComposition = self.__sortTopicComposition(topicComposition)

        # Add document to its top 3 topics' doc list
        stopStep = min(3, len(topicComposition))
        for idx in range(0, stopStep):
            # Append document to the corresponding cluster identified by topic id
            # clusters[maxIdx].docs.append(globals.PUBMED_SEARCH_URL + str(docId))
            clusters[topicComposition[idx][0]].docs.add((docInfo.uiText, topicComposition[idx][1]))
            # Add its year of publishment - need to normalise
            clusters[topicComposition[idx][0]].years.add(docInfo.year)
        
    def __getMaxTopicIndex(self, topicComposition):
        return max(topicComposition, key=itemgetter(1))[0]
            
    def __sortTopicComposition(self, topicComposition):
        return sorted(topicComposition, key=itemgetter(1), reverse=True)

# class KMeansClusterer:
