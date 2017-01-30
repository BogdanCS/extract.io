import sys
sys.path.insert(0, '/home/bogdan/dev/COMP30040/extract.io/src')

from topicmanager import TopicManager
if __name__ == "__main__":
    req1 = {'keywords': 'diabetes',
            'startDate': '01/03/2010',
            'endDate': '03/07/2016',
            'limit' : 10}

    topics = TopicManager().getTopics(req1)

    for topic, extracted in topics.iteritems():
        for word in topic.words:
            print word,
        print
        for doc in extracted.docs:
            print doc
        print extracted.score
