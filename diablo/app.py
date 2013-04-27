import os

from flask import Flask, json, Response
from lxml import html
import redis
import requests


redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)
SERVER_STATUS_URL = 'http://us.battle.net/d3/en/status'
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<pre><a href="/status.json">/status.json</a></pre>'


@app.route('/status.json')
def status():
    status = redis.get('status')
    if status is None:
        status = json.dumps(get_status())
        redis.setex('status', status, 10)
    return Response(status, mimetype='application/json')


def get_status():

    res = requests.get(SERVER_STATUS_URL)

    root = html.document_fromstring(res.text)
    status = dict()

    for box in root.find_class('box'):
        temp = dict()
        category = box.find_class('header-3')[0].text_content()

        for server in box.find_class('server'):
            server_name = server.find_class('server-name')[0].text_content().strip()

            if len(server_name):
                temp[camelcase(server_name)] = server.find_class('status-icon')[0].get('data-tooltip')

        status[camelcase(category)] = temp

    return status


def camelcase(s):
    s = s.lower()
    words = s.split(' ')
    words = [words[0]] + [w.capitalize() for w in words[1:]]
    return ''.join(words)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
