#This should be moved in the same module with TopicInformation, DocInfo

class LinkInformation(object):
    def __init__(self, source, target, initValue):
        self.source = source
        self.target = target
        self.value = initValue
    def addToValue(value):
        self.value += value
