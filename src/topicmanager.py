import logging

import globals
from documentclusterer import TopTopicClusterer
from topicinformation import TopicInformation
from linkinformation import LinkInformation
from topiclinker import SimpleTopicLinker

class TopicManager():

    def getTopics(self, model, docs, linker=SimpleTopicLinker()):
        logging.info("getTopics()")
        
        # Extract basic information from our document set about each topic
        # We keep the model as a global variables so we don't have to load it each time
        (topics, links) = self.__getTopicsBasicInfo(model, docs, linker)
        
        # Drop the topic id keys as we don't need them anymore
        # Convert the binary tree container in which we store years
        # to a regular list so we can pass it to the UI
        topic_list = [] 
        for v in topics.values():
            v.finaliseYears()
            topic_list.append(v)
        
        # Convert link list dictionary to a simple list of LinkInformation
        # Drop weak links
        link_list = []
        for (source, target), values in links.iteritems():
            if(linker.strongLink(values)):
                link_list.append(LinkInformation(source, 
                                                 target, 
                                                 linker.getFinalValue(values)))
        
        return (topic_list, link_list)
        
    def __getTopicsBasicInfo(self, model, docs, linker):
        # key - topic id
        # value - TopicInformation
        topics = {}
        # key - (source,target) where source < target, 
        # value - (total link strenght, total links)
        links = {}
        
        for docId, docInfo in docs.iteritems():
            # topicComposition a list of tuples (topic id, probability)
            topicComposition = model.getTopicComposition(docInfo)

            linker.getLinks(topicComposition, links)

            for topicId, prob in topicComposition:
                if(topicId not in topics):
                    nameTokens = model.getTopicName(topicId) 
                    wordsProb = model.getTopicWords(topicId)
                    topics[topicId] = TopicInformation(topicId, nameTokens, wordsProb)
                # Update topic score 
                topics[topicId].score = topics[topicId].score + (prob/len(docs));
                
            TopTopicClusterer().getDocClusters(docId, docInfo, model, topics)
                
        return (topics, links)
