import logging

import globals
from decimal import *
from documentclusterer import TopTopicClusterer
from topicinformation import TopicInformation
from linkinformation import LinkInformation
from topiclinker import SimpleTopicLinker
from tsforecaster import TSForecaster

class TopicManager():

    def getTopics(self, model, docs, linker=SimpleTopicLinker(), forecaster=TSForecaster(), summary = True):
        logging.info("getTopics()")
        
        # Extract basic information from our document set about each topic
        # We keep the model as a global variables so we don't have to load it each time
        (topics, links) = self.__getTopicsBasicInfo(model, docs, linker, summary)
        
        # Convert the dictionaries in which we store years counts and docs ids
        # to a regular list so we can pass it to the UI
        # Also get forecast for subsequent years
        for v in topics.itervalues():
            forecaster.getForecast(v)

            v.finaliseYears()
            v.finaliseDocs()
        
        # Convert link list dictionary to a simple list of LinkInformation
        # Drop weak links
        link_list = []
        noDocs = len(docs)
        for (source, target), values in links.iteritems():
            if(linker.strongLink(values, noDocs)):
                link_list.append(LinkInformation(source, 
                                                 target, 
                                                 linker.getFinalValue(values)))
        
        return (topics, link_list)
                
    def __updateWordProbSum(self, wordsProb, wordProbAvg):
        for word, prob in wordsProb:
            if word in wordProbAvg:
                wordProbAvg[word] = wordProbAvg[word] + prob
            else:
                wordProbAvg[word] = prob
        
    def __getTopicsBasicInfo(self, model, docs, linker, summary = True):
        # key - topic id
        # value - TopicInformation
        topics = {}
        # key - (source,target) where source < target, 
        # value - (total link strenght, total links)
        links = {}
        clusterer = TopTopicClusterer()
        # average word/topic probability
        wordProbSum = {}
        for docId in docs.keys():
            docInfo = docs[docId]
            # topicComposition a list of tuples (topic id, probability)
            topicComposition = model.getTopicComposition(docInfo)
            if len(topicComposition) == 0:
                logging.warn("Ignore document pmid=" + str(docId))
                del docs[docId]
                continue

            logging.info("Processing document pmid=" + str(docId))
            
            linker.getLinks(topicComposition, links)

            for topicId, prob in topicComposition:
                if(topicId not in topics):
                    nameTokens = model.getTopicName(topicId) 
                    wordsProb = model.getTopicWords(topicId)
                    topics[topicId] = TopicInformation(topicId, nameTokens, wordsProb)
                    if summary:
                        self.__updateWordProbSum(wordsProb, wordProbSum)
                # Update topic score 
                topics[topicId].score = topics[topicId].score + (prob/len(docs));
            if summary:
                clusterer.updateDocClusters(docId, docInfo, model, topics, topicComposition)
        
        if summary:
            # Set summaries
            for docId, docInfo in docs.iteritems():
                noTopics = len(topics)
                wordProbAvg = {k: Decimal(v) / Decimal(noTopics) for k, v in wordProbSum.iteritems()}
                docInfo.setSummariesDec(topics, wordProbAvg)
            # Normalise counts based on the total number of documents for each attribute(e.g year)
            clusterer.normaliseCounts(topics)
        return (topics, links)
