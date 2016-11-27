from Bio import Entrez

import sys

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
	
def search(maxNoArticles, query):
    Entrez.email = 'bogdan.stoian11@gmail.com'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax=maxNoArticles,
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'bogdan.stoian11@gmail.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

if __name__ == '__main__':
    (maxNoArticles, topic) = handleCmdArg()
    results = search(maxNoArticles, topic)
    id_list = results['IdList']
    papers = fetch_details(id_list)
    for i, paper in enumerate(papers):
        print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
    
	# dump everything in a database just in case
	# feed the papers array in another script

	import io
    	import json
    	with io.FileIO("foobar.txt", "w") as file:
	    file.write(json.dumps(paper, indent=2, separators=(',', ':')))

