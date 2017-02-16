import json
import os
import traceback
import logging

import webapp2
from google.appengine.ext.webapp import template
#from paste import httpserver
from topicmanager import TopicManager

#import jinja2
#JINJA_ENVIRONMENT = jinja2.Environment(
#    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#    extensions=['jinja2.ext.autoescape'],
#    autoescape=True)

class MainPage(webapp2.RequestHandler):
    """ Renders the main template. """

    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
        #template = JINJA_ENVIRONMENT.get_template(path)
        #self.response.out.write(template.render(template_values))


class RPCNewSearchHandler(webapp2.RequestHandler):
    """ Process RPC requests for new search. """

    def get(self):

        try:
            req = { 'keywords': self.request.get('keywords'),
                    'startDate': self.request.get('start_date'),
                    'endDate': self.request.get('end_date', '0'),
                    'limit': self.request.get('limit')}

 	    train = [['sports football', 'this talks about football, or soccer, with a goal and a ball'],
 	   	     ['sports rugby', 'here we have some document where we do a scrum and kick the ball'],
 	   	     ['music concerts', 'a venue with loud music and a stage'],
 	   	     ['music instruments', 'thing that have strings or keys, or whatever']]
 	   
 	    test = [['music', 'the stage was full of string things'],
 	            ['sports', 'we kick a ball around'],
 	            ['rugby', 'now add some confusing sentence with novel words what is happening']]
 	  
 	    import labellda
 	    
 	    stmt = labellda.STMT('test_model')
 	    stmt = labellda.STMT('test_model', epochs=400, mem=14000)
 	    
 	    train_labels, train_space = zip(*train)
            print train_labels
            print train_space
 	    test_labels, test_space = zip(*test)
 	    
 	    stmt.train(train_space, train_labels)
 	    stmt.test(test_space, test_labels)
 	    
 	    y_true, y_score = stmt.results(test_labels, array=True)
 	    
 	    from sklearn.metrics import average_precision_score
 	    print y_true
 	    print y_score
 	    print test_labels
 	    print test_space
 	    print(average_precision_score(y_true, y_score))
            # Retrieve topics and links
            # (topics, links) = TopicManager().getTopics(req)

            #for extracted in topics:
            #    #for word in extracted.words:
            #    #    print word,
            #    #print
            #    for doc in extracted.docs:
            #        print doc
            #    #print extracted.score
            #for link in links:
            #    print link.source,
            #    print link.target,
            #    print link.value

            # print json.dumps({"topics" : topics,
            #                  "links"  : links}, default=lambda o: o.__dict__)
            
            # Set json response
            # self.response.out.write(json.dumps({"topics" : topics,
                                                #"links"  : links}, default=lambda o: o.__dict__))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))

#class RPCGetXHandler(webapp.RequestHandler):
#    """ Process RPC requests for getting X. """

application = webapp2.WSGIApplication([('/rpcNewSearch', RPCNewSearchHandler),
                                       ('/.*', MainPage)], debug=True)

if __name__ == "__main__":
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
