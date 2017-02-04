import json
import sys
sys.path.insert(0, '/home/bogdan/dev/COMP30040/extract.io/src')

from topicmanager import TopicManager
if __name__ == "__main__":
    req1 = {'keywords': 'diabetes',
            'startDate': '01/03/2010',
            'endDate': '03/07/2016',
            'limit' : 50}

    topics = TopicManager().getTopics(req1)

    for extracted in topics:
        for word in extracted.words:
            print word,
        print
        for doc in extracted.docs:
            print doc
	for year in extracted.years:
	    print year
        print extracted.score

    print json.dumps({"topics" : topics}, default=lambda o: o.__dict__)
