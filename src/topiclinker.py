class SimpleTopicLinker:
    
    def getLinks(self, topicComposition, links):
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
    
    def strongLink(self, values):
        if (values[1]<50): # This shouldn't be hard coded
            return False
        return True
        
    def getFinalValue(self, values):
        return values[0]*values[1]
                
