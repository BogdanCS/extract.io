import logging
import gensim
import hunspell

from globals import Globals
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter
from documentclusterer import TopTopicClusterer
from documentinformation import DocumentInformation
from topicinformation import TopicInformation
from linkinformation import LinkInformation
from topiclinker import SimpleTopicLinker

class TopicManager():

    def getTopics(self, docs):
        logging.info("getTopics()")
        
        # Extract basic information from our document set about each topic
        # We keep the model as a global variables so we don't have to load it each time
        (topics, links) = self.__getTopicsBasicInfo(Globals.MODEL, docs)
        
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
            if(SimpleTopicLinker().strongLink(values)):
                link_list.append(LinkInformation(source, 
                                                 target, 
                                                 SimpleTopicLinker().getFinalValue(values)))
        
        return (topic_list, link_list)
        
    def __getTopicsBasicInfo(self, model, docs):
        # key - topic id
        # value - TopicInformation
        topics = {}
        # key - (source,target) where source < target, 
        # value - (total link strenght, total links)
        links = {}
        
        for docId, docInfo in docs.iteritems():
            # topicComposition a list of tuples (topic id, probability)
            topicComposition = model.get_document_topics(docInfo.bow)

            SimpleTopicLinker().getLinks(topicComposition, links)

            for topicId, prob in topicComposition:
                if(topicId not in topics):
                    words = self.__getTopicWords(model, topicId) 
                    topics[topicId] = TopicInformation(topicId, words)
                # Update topic score 
                topics[topicId].score = topics[topicId].score + (prob/len(docs));
                
            TopTopicClusterer().getDocClusters(docId, docInfo, model, topics)
                
        return (topics, links)
        
    def __getTopicWords(self, model, topicId):
        output = []

        topWords = model.show_topic(topicId, topn=5)
        for word, prob in topWords:
            output.append(word)

        return output
