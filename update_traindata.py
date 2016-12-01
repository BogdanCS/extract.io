import gensim
import io

from documentretriever import PubmedRetriever
from malletconverter import MalletConverter

if __name__ == '__main__':
    pubmed = PubmedRetriever()
    papers = pubmed.getDocumentsIf("diabetes", 1000)
    
    malletCorpus = MalletConverter.toMallet(papers, 'PMID', 'AbstractText')

    with io.FileIO("corpus_training.txt", "w") as file:
        file.write(malletCorpus.encode('utf8'))
        
    corpus = gensim.corpora.MalletCorpus('corpus_training.txt')
    model = gensim.models.LdaModel(corpus, id2word=corpus.id2word, alpha='auto', num_topics=25)
    model.save('corpus_training.lda')
    
    print model.show_topics(num_topics=5, num_words=5)
        
