import logging
import gensim
import hunspell

from globals import Globals
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter
from documentclusterer import TopTopicClusterer
from topicinformation import TopicInformation

class TopicManager():
    #def __init__(self):
        # to update with default model
        # to update with a more clever cache
        # self.cachedTopicModel = []

    def getTopics(self, req):
        logging.info("getTopics()")
        
        pubmed = PubmedRetriever()
        # TODO - Add the timestamps
        # Retrieve abstracts
        papers = pubmed.getDocumentsIf(req['keywords'], req['limit'])

        # Create preprocesser
        stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
        # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
        prepro = PubmedPreprocesser(stemmer)
        
        bowConverter = gensim.corpora.Dictionary()
        # Do we need to merge with initial corpus?
        
        # Transform each document in a bag of words, identify the bag of words by the initial doc id
        doc_bow = {}
        for paper in papers:
            # We might want to set allow_update = true
            # Swallow exceptions due to invalid data
            try:
                docId = MalletConverter.getDocId(Globals.PUBMED_ID_FIELD_NAME, paper)
                docData = bowConverter.doc2bow(MalletConverter.getDataAsString(
                    Globals.PUBMED_ABSTRACT_FIELD_NAME, prepro, paper ).split())
                doc_bow[docId] = docData
            except StopIteration:
                logging.info("Abstranct not found")
                print "Abstract not found"

            #doc_bow.append(bowConverter.doc2bow(MalletConverter.getDataAsString(paper, prepro, 'AbstractText').split()))

        # Create bow dictionary
        # doc_bow.add_documents(doc_low)

        # malletCorpus = MalletConverter.toMallet(papers, prepro, 'PMID', 'AbstractText')
        
        # TODO - multiple models
        # have this loaded?
        model = gensim.models.LdaModel.load(Globals.TRAINED_MODEL_PATH)
        # TODO - update async model.update(corpus)
        
        # TopicBasicInfo -> ExtractedBasicInfo mapping
        # Retrieve topic basic information from our document set
        topics = self.__getTopicsBasicInfo(model, doc_bow)
        # Extract information about topics
        # is this copy necessary? topics = self....
        self.__getTopicsExtractedInfo(model, doc_bow, topics)
        
        # Drop the topic ids as we don't need them anymore
        topic_list = [ v for v in topics.values() ]
        return topic_list
        
            # we might be interested in max topic, we might not - this could be decided in the UI
        #    topicComposition = model.get_document_topics(bow)
        #    for topicId, prob in topicComposition:
        #        if(
            
    def __getTopicsBasicInfo(self, model, doc_bow):
        topics = {}
        for bow in doc_bow.itervalues():
            # topicComposition a list of tuples (topic id, probability)
            topicComposition = model.get_document_topics(bow)
            for topicId, prob in topicComposition:
                if(topicId not in topics):
                    words = self.__getTopicWords(model, topicId) 
                    topics[topicId] = TopicInformation(words)
                # Update topic score 
                topics[topicId].score = topics[topicId].score + (prob/len(topicComposition))
                
        return topics
        
    def __getTopicsExtractedInfo(self, model, doc_bow, topics):
        # For each topic get the documents where that topic is predominant
        TopTopicClusterer().getDocClusters(doc_bow, model, topics)
            
    def __getTopicWords(self, model, topicId):
        output = []

        topWords = model.show_topic(topicId, topn=5)
        for word, prob in topWords:
            output.append(word)

        return output
