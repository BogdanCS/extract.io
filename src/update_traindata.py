import gensim
import io
import hunspell

#from nltk.stem import *

from globals import Globals
from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter
from documentclusterer import TopTopicClusterer

if __name__ == '__main__':
    pubmed = PubmedRetriever()
    #todo update
    papers = pubmed.getDocumentsIf("diabetes", 10)
    
    stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
    # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
    prepro = PubmedPreprocesser(stemmer)
    # TODO make AbstractText global constant
    malletCorpus = MalletConverter.xmlToMallet(papers, prepro, 'PMID', 'AbstractText')

    # database ?
    with io.FileIO(Globals.CORPUS_PATH, "w") as file:
        file.write(malletCorpus.encode('utf8'))
        
    corpus = gensim.corpora.MalletCorpus(Globals.CORPUS_PATH)
    model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=100, iterations=200)
    model.save(Globals.TRAINED_MODEL_PATH)
    
    # either get abbreviatons from first occurence in text or get it from some web service
    
    # group abstract per topic
    #for i in range(0,10):
    #    print model.get_document_topics(mm[i])
    gensim.corpora.mmcorpus.MmCorpus.serialize('corpus_training.mm', corpus)
    mm = gensim.corpora.mmcorpus.MmCorpus('corpus_training.mm') # `mm` document stream now has random access
    #clusterer = TopTopicClusterer()
    #clusters = clusterer.getClusters(mm, model)
    
    # call termine for each group
    # for cluster in clusters:

    # debugging
    ### ignore this and then with the trained model iterate over other documents?
    #for key, val in clusters.iteritems():
    #    for idx in val:
    #        print idx
    #        print papers[idx]
    #        # how to go back from this index to the original document?
    #        # check mallet documentation maybe we can use the id somehow

    print model.show_topic(0)
    print model.show_topics(num_topics=5, num_words=5)
        
