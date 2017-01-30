import json
import os
import traceback
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from topicmanager import TopicManager

class MainPage(webapp.RequestHandler):
    """ Renders the main template. """

    def get(self):

        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class RPCNewSearchHandler(webapp.RequestHandler):
    """ Process RPC requests for new search. """

    def get(self):

        try:
            req = { 'keywords': self.request.get('keywords'),
                    'startDate': self.request.get('start_date'),
                    'endDate': self.request.get('end_date', '0'),
                    'limit': self.request.get('limit')}

            # Retrieve topics
            topics = TopicManager().getTopics(req)

            # Set response in json format
            self.response.out.write(json.dumps({"topicsInfo":topics}))

        except Exception, e:
            traceback.print_exc()
            self.response.out.write(json.dumps({"error":str(e)}))

#class RPCGetXHandler(webapp.RequestHandler):
#    """ Process RPC requests for getting X. """
    
application = webapp.WSGIApplication([('/rpcNewSearch', RPCNewSearchHandler),
                                      ('/.*', MainPage)], debug=False)

if __name__ == "__main__":
    run_wsgi_app(application)
