import json
import sys
sys.path.insert(0, '/home/bogdan/dev/COMP30040/extract.io/src')

import globals
from topicmanager import TopicManager
from topicmodel import LDATopicModel, LLDATopicModel
from documentmanager import DocumentManager

if __name__ == "__main__":
    req = {'keywords': 'diabetes',
            'startDate': '1361566331',
            'endDate': '1456174331',
            'limit' : 100,
            'model' : 'LDA'}

    DocumentManager().getDocuments(req)
    print globals.PROCESSED_CACHED_CORPUS
    # This could be model factory
    model = None
    if(req['model'] == 'LLDA'):
        model = LLDATopicModel(globals.LLDA_MODEL, globals.LLDA_LABEL_INDEX, globals.PROCESSED_CACHED_CORPUS)
    else:
        model = LDATopicModel(globals.LDA_MODEL)

    # Retrieve topics and links
    (topics, links) = TopicManager().getTopics(model, globals.PROCESSED_CACHED_CORPUS)

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
