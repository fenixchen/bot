# -*- coding: UTF-8 -*-

from flask import Flask, jsonify, request, make_response, abort
import logging
import os
import time
import botpath

print("=> Importing tensorflow...")

import tensorflow as tf

tf.logging.set_verbosity(tf.logging.ERROR)

print("=> Importing rasa...")
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent

app = Flask(__name__, static_url_path='')


def get_request_arg(req, field):
    req_dict = req.args.to_dict()
    if field in req_dict:
        return req_dict[field]
    else:
        return None


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.route('/', methods=['GET'])
def index():
    return app.send_static_file("index.html")


@app.route("/bot/ask")
def ask():
    response = {}
    question = get_request_arg(request, "question")
    session_id = get_request_arg(request, "session_id")
    answers = agent.handle_message(question, sender_id=session_id)
    answers_text = ''
    for msg in answers:
        if 'text' in msg:
            answers_text += msg['text'] + '~'
    if len(answers_text) > 0:
        answers_text = answers_text[:len(answers_text) - 1]
    else:
        answers_text = "No answer"

    response['answer'] = answers_text

    response['time'] = time.time()
    return make_response(jsonify({'response': response}, 200))


if __name__ == '__main__':
    print("=> HC NLU Bot Initializing...")
    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)
    agent = Agent.load(botpath.DIALOGUE_PATH, interpreter=interpreter)
    app.debug = True
    print("=> Starting http server...")
    app.run(host='0.0.0.0', port=80, use_reloader=False)
