import logging
import time
import math
from collections import Counter
from linkinformation import LinkInformation

class SimpleTopicLinker:
    
    def getLinks(self, topicComposition, links):
        logging.info("Start getting links")
        start = time.time()
        # key - (source,target) where source < target, 
        # value - (total link strenght, total links)
        for idx, (topicId1, prob1) in enumerate(topicComposition[:-1], start=1):
            # idx is one step ahead of the actual index
            for (topicId2, prob2) in topicComposition[idx:]:
                source = min([topicId1, topicId2])
                target = max([topicId1, topicId2])
                if (source,target) not in links:
                    links[(source,target)] = (min([prob1, prob2]), 1)
                else:
                    links[(source,target)] = (links[(source,target)][0] + min([prob1, prob2]),
                                              links[(source,target)][1] + 1) 
        end = time.time()
        logging.info("Stop getting links. Time(sec): ")
        logging.info(end-start)
    
    def strongLink(self, values):
        if (values[1]<50): # This shouldn't be hard coded
            return False
        return True
        
    def getFinalValue(self, values):
        return values[0]*values[1]
                
class DummyTopicLinker:
    def getLinks(self, topicComposition, links):
        logging.info("Not computing links")
        
class ComparisonTopicLinker:
    def getLinks(self, sourceTopics, targetTopics, links):
        # Only keep the maximum value link from each target
        for targetTopic in targetTopics:
            maxLink = LinkInformation (-1, -1, 0.0) 
            for sourceTopic in sourceTopics:
                value = self.getCosineSim(sourceTopic.wordsProb, 
                                          targetTopic.wordsProb)
                if (value > maxLink.value):
                    maxLink = LinkInformation(sourceTopic.uid,
                                              targetTopic.uid,
                                              value) 
            links.append(maxLink)
                    
    def getCosineSim(self, topicA, topicB):
        countsA = self.getCounts(topicA)
        countsB = self.getCounts(topicB)
        
        terms = set(countsA).union(countsB)
        dotprod = sum(countsA.get(k, 0) * countsB.get(k, 0) for k in terms)
        magA = math.sqrt(sum(countsA.get(k, 0)**2 for k in terms))
        magB = math.sqrt(sum(countsB.get(k, 0)**2 for k in terms))
        cosSim = dotprod / (magA*magB)

        return cosSim * 170 
            
    def getCounts(self, topicA):
        c = Counter()
        for k,v in topicA:
            c.update({k:v})
        return c
        
    
