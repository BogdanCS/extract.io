import sys

from documentretriever import PubmedRetriever

def handleCmdArg():
    maxNoArticles = 0
    topic = ''
    try:
    	maxNoArticles = sys.argv[1]
    except IndexError:
	print("Please supply a maximum number of articles to be fetched")
    try:
	idx = 2
	while(True):
	    if (idx == 2):
		topic = sys.argv[idx]
	    else:
		term = sys.argv[idx]
		topic += ' AND ' + term
	    idx=idx+1
    except IndexError:
	    if (topic == ''):
		print("Please a supply a topic")
    return (maxNoArticles,topic)

if __name__ == '__main__':
    (maxNoArticles, topic) = handleCmdArg()
    pubmedRet = PubmedRetriever()
    papers = pubmedRet.getDocumentsIf(topic, maxNoArticles)
    for i, paper in enumerate(papers):
        print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
        
    # dump everything in a database just in case
    # feed the papers array in another script
    # print paper
    # print paper['MedlineCitation']['DateCompleted']['Year']
    # import io
    # import json
    # with io.FileIO("foobar.txt", "w") as file:
    # dict = json.loads(json.dumps(paper, indent=2, separators=(',', ':')))
    # print dict
    # print dict['MedlineCitation']['DateCompleted']['Year']

