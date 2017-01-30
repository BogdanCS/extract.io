class TopicBasicInfo(object):
    def __init__(self, idx):
        self.idx = idx
        self.words = []

    # We could have done this in the constructor but
    # we want the TopicBasicInfo construction to be cheap
    # since we are sometimes using it only as a wrapper for the idx
    def getTopicWords(self, model):
        topWords = model.show_topic(self.idx, topn=5)
        for word, prob in topWords:
            self.words.append(word)
            
    def __hash__(self):
        return hash((self.idx))
        
    def __eq__(self, other):
        return self.idx == other.idx

    def __ne__(self, other):
        return not self.__eq__(other)

class TopicExtractedInfo(object):
    def __init__(self):
        self.docs = []
        self.score = 0

    
