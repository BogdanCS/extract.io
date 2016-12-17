import gensim
import io
import hunspell

#from nltk.stem import *

from documentretriever import PubmedRetriever
from preprocesser import PubmedPreprocesser
from malletconverter import MalletConverter

if __name__ == '__main__':
    pubmed = PubmedRetriever()
    papers = pubmed.getDocumentsIf("diabetes", 10000)
    
    stemmer = hunspell.HunSpell('/usr/share/myspell/dicts/en_GB.dic', '/usr/share/myspell/dicts/en_GB.aff') # dictionary based stemmer
    # stemmer = SnowballStemmer("english") # algorithmic(Porter) stemmer
    prepro = PubmedPreprocesser(stemmer)
    
    malletCorpus = MalletConverter.toMallet(papers, prepro, 'PMID', 'AbstractText')

    # database ?
    with io.FileIO("corpus_training.txt", "w") as file:
        file.write(malletCorpus.encode('utf8'))
        
    corpus = gensim.corpora.MalletCorpus('corpus_training.txt')
    model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=100, iterations=200)
    model.save('corpus_training.lda')
    
    # todo print text before preprocessing to check how good the pre processing is
    # write function to expand abbreviations
    # either get abbreviatons from first occurence in text or get it from some web service

    print model.show_topic(0)
    print model.show_topics(num_topics=5, num_words=5)
        
