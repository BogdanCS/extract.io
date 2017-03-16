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
from topiclinker import DummyTopicLinker, ComparisonTopicLinker
from documentmanager import DocumentManager
from tsforecaster import DummyTSForecaster

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
            req = { 'keywords': self.request.get('keywords'),
                    'startDate': self.request.get('start_date'),
                    'endDate': self.request.get('end_date'),
                    'limit': self.request.get('limit')}
            filename = req['keywords'] + "_" + req['startDate'] + "_" + req['endDate'] + "_" + req['limit']

            if (os.path.isfile(globals.CACHE_PATH + filename + "_dual_lock") or
                os.path.isfile(globals.CACHE_PATH + filename + "_LLDA_lock")):
                self.response.out.set_status(500)
                return
            elif (os.path.isfile(globals.CACHE_PATH + filename + "_dual")):
                with open(globals.CACHE_PATH + filename + "_dual", 'r') as infile:
                    data = json.load(infile)
                # Set json response
                self.response.out.write(json.dumps(data, default=lambda o: o.__dict__))
                return

            with open(globals.CACHE_PATH + filename + "_dual_lock", 'w') as lockfile:
                lockfile.write("Lock")
                
            # Recreate PROCESSED_CACHED_CORPUS
            DocumentManager().getDocuments(req) 
            
            lldamodel = LLDATopicModel(globals.LLDA_MODEL, globals.PROCESSED_CACHED_CORPUS)
            print "ce plm"
            ldamodel = LDATopicModel(globals.LDA_MODEL)
            print "ce plm2"
                
            # Retrieve topics and links
            (ldaTopics, _) = TopicManager().getTopics(ldamodel, 
                                                      globals.PROCESSED_CACHED_CORPUS,
                                                      DummyTopicLinker(), DummyTSForecaster(), False)
            (lldaTopics, _) = TopicManager().getTopics(lldamodel, 
                                                       globals.PROCESSED_CACHED_CORPUS,
                                                       DummyTopicLinker(), DummyTSForecaster(), False)
            
            # We need to make sure the UIDs are unique between the two sets of topics
            lldaTopicsNew = {}
            for topicId, topicInfo in lldaTopics.iteritems():
                topicInfo.uid = -topicInfo.uid
                lldaTopicsNew[-topicId] = topicInfo
                
            # Compute cosine similarity between topics and then get links
            # Links are from LLDA topic(source to LDA topic(target)
            links = []
            ComparisonTopicLinker().getLinks(lldaTopicsNew.values(), ldaTopics.values(), links)
            
            topics = dict(ldaTopics, **lldaTopicsNew)
            #topics = ldaTopics + lldaTopics

            #ldaEvals = ModelEvaluator().getMeasures(ldaModel, ldaTopics)
            #lldaEvals = ModelEvalutor().getMeasures(lldaModel, lldaTopics)

            # Dump this to file and retrieve it (i.e cache)
            #print json.dumps({"topics" : topics,
            #                  "links"  : links}, default=lambda o: o.__dict__)
            
            with open(globals.CACHE_PATH + filename + "_dual", 'w') as outfile:
                json.dump({"topics" : topics,
                            "links"  : links}, 
                          outfile,
                          default=lambda o: o.__dict__
                          )
                
            os.remove(globals.CACHE_PATH + filename + "_dual_lock")

            # Set json response
            self.response.out.write(json.dumps({"topics" : topics,
                                                "links"  : links}, default=lambda o: o.__dict__))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))
        
#class RPCNewModelHandler(webapp2.RequestHandler):
#    """ Process RPC requests for new model. """
#    """ This bypasses the corpus retrieval and preprocessing """
#    """ It assummes that a cached corpus exists """
#
#    def get(self):
#        try:
#            if not globals.PROCESSED_CACHED_CORPUS:
#                raise Exception("No corpus has been processed")
#        
#            req = { 'model' : self.request.get('model')}
#            
#            # This could be model factory
#            model = None
#            if(req['model'] == 'LLDA'):
#                model = LLDATopicModel(globals.LLDA_MODEL, globals.PROCESSED_CACHED_CORPUS)
#            else:
#                model = LDATopicModel(globals.LDA_MODEL)
#
#            # Retrieve topics and links
#            (topics, links) = TopicManager().getTopics(model, globals.PROCESSED_CACHED_CORPUS)
#            
#        except Exception, e:
#            traceback.print_exc()
#            self.response.out.write(json.dumps({"error":str(e)}))
        
class RPCNewSearchHandler(webapp2.RequestHandler):
    """ Process RPC requests for new search. """

    def get(self):
        try:
            req = { 'keywords': self.request.get('keywords'),
                    'startDate': self.request.get('start_date'),
                    'endDate': self.request.get('end_date'),
                    'limit': self.request.get('limit'),
                    'model': self.request.get('model')}
            filename = req['keywords'] + "_" + req['startDate'] + "_" + req['endDate'] + "_" + req['limit'] + "_" + req['model']

            # Need to check DUAL for LLDA
            if (os.path.isfile(globals.CACHE_PATH + filename + "_lock")):
                self.response.out.set_status(500)
                return
            elif (os.path.isfile(globals.CACHE_PATH + filename)):
                with open(globals.CACHE_PATH + filename, 'r') as infile:
                    data = json.load(infile)
                # Set json response
                self.response.out.write(json.dumps(data, default=lambda o: o.__dict__))
                return
                
            with open(globals.CACHE_PATH + filename + "_lock", 'w') as lockfile:
                lockfile.write("Lock")
                
            # Recreate PROCESSED_CACHED_CORPUS
            DocumentManager().getDocuments(req) 
            
            # This could be model factory
            model = None
            if(req['model'] == 'LLDA'):
                model = LLDATopicModel(globals.LLDA_MODEL, globals.PROCESSED_CACHED_CORPUS)
            else:
                model = LDATopicModel(globals.LDA_MODEL)
                
            # Retrieve topics and links
            (topics, links) = TopicManager().getTopics(model, globals.PROCESSED_CACHED_CORPUS)

            print model.getPerplexity()

            with open(globals.CACHE_PATH + filename, 'w') as outfile:
                json.dump({"topics" : topics,
                            "links"  : links,
                            "docs"   : globals.PROCESSED_CACHED_CORPUS}, 
                          outfile,
                          default=lambda o: o.__dict__
                          )
            
            os.remove(globals.CACHE_PATH + filename + "_lock")
                
            # Set json response
            self.response.out.write(json.dumps({"topics" : topics,
                                                "links"  : links,
                                                "docs"   : globals.PROCESSED_CACHED_CORPUS}, default=lambda o: o.__dict__))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))


application = webapp2.WSGIApplication([('/rpcNewSearch', RPCNewSearchHandler),
#                                       ('/rpcNewModel', RPCNewModelHandler),
                                       ('/rpcNewSearchDualView', RPCNewSearchDualViewHandler),
                                       ('/.*', MainPage)], debug=True)

if __name__ == "__main__":
    application.run()
    #httpserver.serve(application, host='127.0.0.1', port='8080')
