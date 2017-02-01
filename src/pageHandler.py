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

            # Retrieve topics
            topics = TopicManager().getTopics(req)

            #for extracted in topics:
            #    for word in extracted.words:
            #        print word,
            #    print
            #    for doc in extracted.docs:
            #        print doc
            #    print extracted.score

            print json.dumps({"topics" : topics}, default=lambda o: o.__dict__)
            
            # Set json response
            self.response.out.write(json.dumps({"topics" : topics}, default=lambda o: o.__dict__))

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
