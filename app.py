import os

from flask import Flask, jsonify
from lxml import html
import requests
import sendgrid


SERVER_STATUS_URL = 'http://us.battle.net/d3/en/status'
last_status = None
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/status.json')
def status():
    status = get_status()
    return jsonify(status)


@app.route('/email')
def email():

    global last_status

    status = get_status()['americas']['gameServer']

    if last_status is None:
        last_status = status
        return'first run'
    elif status == last_status:
        return 'no change'

    last_status = status

    user_address = 'dhazinski@gmail.com'
    sender_address = "app5257489@heroku.com"
    subject = "Diablo Server: %s" % status
    body = " "

    s = sendgrid.Sendgrid(os.environ.get('SENDGRID_USERNAME'),
                          os.environ.get('SENDGRID_PASSWORD'),
                          secure=True)
    message = sendgrid.Message(sender_address, subject, body)
    message.add_to(user_address)

    s.web.send(message)


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
    app.run(host='0.0.0.0', port=port, debug=False)
