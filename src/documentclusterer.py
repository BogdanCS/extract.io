from abc import ABCMeta, abstractmethod   
from operator import itemgetter
import math
import logging

import globals
#class DocumentClusterer:
#    __metaclass__ = ABCMeta
#
#    @abstractmethod
#    # Returns pairs of cluster index - list of indexes of original documents
#    def getClusters(self, bowList, modelFeatures) : pass
    

class TopTopicClusterer:

    def __init__(self):
        # For each year keep a count of how many documents we have in the corpus
        self.docsPerYear = {}

    def __incrementCount(self, key, dct):
        if(key in dct):
           dct[key] = dct[key] + 1
        else:
           dct[key] = 1
        
    def updateDocClusters(self, docId, docInfo, model, clusters):
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
        stopStep = min(4, len(topicComposition))
        for idx in range(0, stopStep):
            #1. Add topic to current document list
            docInfo.topicList.append(topicComposition[idx][0])
            #2. Append document to the corresponding cluster identified by topic id
            clusters[topicComposition[idx][0]].docs.add((docId, topicComposition[idx][1]))
            #3. Add its year of publishment
            self.__incrementCount(docInfo.year, clusters[topicComposition[idx][0]].years)
            self.__incrementCount(docInfo.year.split('-')[0], self.docsPerYear)
            #clusters[topicComposition[idx][0]].years.add(docInfo.year)
        
    # Turn absolute number of document to percetange of documents out of all the documents
    # published in that year from the corpus
    def normaliseCounts(self, clusters):
        for cluster in clusters.itervalues():
            for yearMonth, count in cluster.years.iteritems():
                cluster.years[yearMonth] = int(math.floor(100 * count / self.docsPerYear[yearMonth.split('-')[0]])) 
            
    def __getMaxTopicIndex(self, topicComposition):
        return max(topicComposition, key=itemgetter(1))[0]
            
    def __sortTopicComposition(self, topicComposition):
        return sorted(topicComposition, key=itemgetter(1), reverse=True)

# class KMeansClusterer:
