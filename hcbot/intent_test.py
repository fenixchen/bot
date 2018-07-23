# -*- coding:utf-8 -*-
import train_nlu
import botpath
from termcolor import cprint


def get_intent(interpreter, message):
    parse_data = interpreter.parse(message)
    intent = parse_data["intent"]
    entities = parse_data["entities"]
    return "intent<{}> entities<{}>".format(intent['name'], entities)


TEST_CASES = {
    '你好': 'intent<greet> entities<[]>',
    'hello': 'intent<greet> entities<[]>',
    '再见': 'intent<goodbye> entities<[]>',
    'bye': 'intent<goodbye> entities<[]>',
    '我是王二小': '',
}

from rasa_core.interpreter import RasaNLUInterpreter

if __name__ == '__main__':
    # train_nlu.train_nlu()
    print("=> HC NLU Bot Initializing...")
    print("Load NLU %s" % botpath.NLU_DATA_FOLDER)
    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)

    for message, result in TEST_CASES.items():
        intent = get_intent(interpreter, message)
        if result != intent:
            cprint("%s => %s failed" % (message, intent), 'red')
        else:
            cprint("%s => %s success" % (message, intent), 'green')
