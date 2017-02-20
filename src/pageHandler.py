import json
import os
import traceback
import logging

import webapp2
from google.appengine.ext.webapp import template
#from paste import httpserver

import globals
from topicmanager import TopicManager
from topicmodel import LDATopicModel, LLDATopicModel
from documentmanager import DocumentManager

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

class RPCNewSearchDualViewHandler(webapp2.RequestHandler):
    def get(self):
        try:
            # Recreate PROCESSED_CACHED_CORPUS
            DocumentManager().getDocuments(req) 
            
            ldamodel = LLDATopicModel(globals.LLDA_MODEL, globals.LLDA_LABEL_INDEX, globals.PROCESSED_CACHED_CORPUS)
            lldamodel = LDATopicModel(globals.LDA_MODEL)
                
            # Retrieve topics and links
            (ldaTopics, ldaLinks) = TopicManager().getTopics(ldamodel, globals.PROCESSED_CACHED_CORPUS)
            (lldaTopics, lldaLinks) = TopicManager().getTopics(lldamodel, globals.PROCESSED_CACHED_CORPUS)
            
        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))
        
#class RPCNewModelDualViewHandler(webapp2.RequestHandler):
#    def get(self):
        
#class RPCDualViewHandler(webapp2.RequestHandler):
#    def get(self):
        
class RPCNewModelHandler(webapp2.RequestHandler):
    """ Process RPC requests for new model. """
    """ This bypasses the corpus retrieval and preprocessing """
    """ It assummes that a cached corpus exists """

    def get(self):
        try:
            if not globals.PROCESSED_CACHED_CORPUS:
                raise Exception("No corpus has been processed")
        
            req = { 'model' : self.request.get('model')}
            
            # This could be model factory
            model = None
            if(req['model'] == 'LLDA'):
                model = LLDATopicModel(globals.LLDA_MODEL, globals.LLDA_LABEL_INDEX, globals.PROCESSED_CACHED_CORPUS)
            else:
                model = LDATopicModel(globals.LDA_MODEL)

            # Retrieve topics and links
            (topics, links) = TopicManager().getTopics(model, globals.PROCESSED_CACHED_CORPUS)
            
        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))
        
class RPCNewSearchHandler(webapp2.RequestHandler):
    """ Process RPC requests for new search. """

    def get(self):
        try:
            req = { 'keywords': self.request.get('keywords'),
                    'startDate': self.request.get('start_date'),
                    'endDate': self.request.get('end_date'),
                    'limit': self.request.get('limit'),
                    'model': self.request.get('model')}

            # Recreate PROCESSED_CACHED_CORPUS
            DocumentManager().getDocuments(req) 
            
            # This could be model factory
            model = None
            if(req['model'] == 'LLDA'):
                model = LLDATopicModel(globals.LLDA_MODEL, globals.LLDA_LABEL_INDEX, globals.PROCESSED_CACHED_CORPUS)
            else:
                model = LDATopicModel(globals.LDA_MODEL)
                
            # Retrieve topics and links
            (topics, links) = TopicManager().getTopics(model, globals.PROCESSED_CACHED_CORPUS)

            #for extracted in topics:
            #    #for word in extracted.nameTokens:
            #    #    print word,
            #    #print
            #    for doc in extracted.docs:
            #        print doc
            #    #print extracted.score
            #for link in links:
            #    print link.source,
            #    print link.target,
            #    print link.value

            print json.dumps({"topics" : topics,
                              "links"  : links}, default=lambda o: o.__dict__)
            
            # Set json response
            self.response.out.write(json.dumps({"topics" : topics,
                                                "links"  : links}, default=lambda o: o.__dict__))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))

#class RPCGetXHandler(webapp.RequestHandler):
#    """ Process RPC requests for getting X. """

application = webapp2.WSGIApplication([('/rpcNewSearch', RPCNewSearchHandler),
                                       ('/rpcNewModel', RPCNewModelHandler),
                                       ('/.*', MainPage)], debug=True)

if __name__ == "__main__":
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
