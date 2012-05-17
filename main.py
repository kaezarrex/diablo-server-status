import json
from lxml import html
import webapp2

from google.appengine.api import urlfetch


SERVER_STATUS_URL = 'http://us.battle.net/d3/en/status'

class MainPage(webapp2.RequestHandler):

    def get(self):

        res = urlfetch.fetch(SERVER_STATUS_URL)
        root = html.document_fromstring(res.content)
        status = dict()

        for box in root.find_class('box'):
            temp = dict()
            category = box.find_class('category')[0].text_content()

            for server in box.find_class('server'):
                server_name = server.find_class('server-name')[0].text_content().strip()

                if len(server_name):
                    temp[camelcase(server_name)] = server.find_class('status-icon')[0].get('data-tooltip')

            status[camelcase(category)] = temp

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(status))


def camelcase(s):
    s = s.lower()
    words = s.split(' ')
    words = [words[0]] + [w.capitalize() for w in words[1:]]
    return ''.join(words)


app = webapp2.WSGIApplication([('/status.json', MainPage)], debug=True)
