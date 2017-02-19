import json
import sys
sys.path.insert(0, '/home/bogdan/dev/COMP30040/extract.io/src')

from globals import Globals
from topicmanager import TopicManager
from topicmodel import LDATopicModel, LLDATopicModel
from documentmanager import DocumentManager

if __name__ == "__main__":
    req = {'keywords': 'diabetes',
            'startDate': '2010/03/10',
            'endDate': '2016/07/03',
            'limit' : 100,
            'model' : 'LLDA'}

    print Globals.PROCESSED_CACHED_CORPUS
    DocumentManager().getDocuments(req)
    print Globals.PROCESSED_CACHED_CORPUS
    
    # This could be model factory
    model = None
    if(req['model'] == 'LLDA'):
        model = LLDATopicModel(Globals.LLDA_MODEL, Globals.LLDA_LABEL_INDEX, Globals.PROCESSED_CACHED_CORPUS)
    else:
        model = LDATopicModel(Globals.LDA_MODEL)

    # Retrieve topics and links
    (topics, links) = TopicManager().getTopics(model, Globals.PROCESSED_CACHED_CORPUS)

    for extracted in topics:
        print extracted.words
        #for word in extracted.words:
        #    print word,
        #print
        for doc in extracted.docs:
            print doc
	for year in extracted.years:
	    print year
        print extracted.score

    print json.dumps({"topics" : topics,
                      "links" : links}, default=lambda o: o.__dict__)
