# -*- coding:utf-8 -*-
import train_nlu
import botpath
from termcolor import cprint


def get_intent(interpreter, message):
    parse_data = interpreter.parse(message)
    intent = parse_data["intent"]
    entities = parse_data["entities"]
    result = "intent<%s>" % intent['name']
    if len(entities) > 0:
        result += ' slot<'
        for entity in entities:
            result += entity['entity'] + ':' + entity['value'] + ' '
        result = result[:-1] + '>'
    return result


TEST_CASES = {
    '你好': 'intent<greet>',
    'hello': 'intent<greet>',
    '再见': 'intent<goodbye>',
    'bye': 'intent<goodbye>',
    '车险': 'intent<insurance>',
    '理赔': 'intent<compensate>',
    '我是王二小': 'intent<inform_name> slot<name:王二小>',
    '我是王健林': 'intent<inform_name> slot<name:王健林>',
    '我叫姚明': 'intent<inform_name> slot<name:姚明>',
    '可以叫我董存瑞': 'intent<inform_name> slot<name:董存瑞>',
    '我的车牌是沪A12345': 'intent<inform_carno> slot<carno:沪A12345>',
    '我的车牌是浙F12345': 'intent<inform_carno> slot<carno:浙F12345>',
    '我的车牌是陕AT8834': 'intent<inform_carno> slot<carno:陕AT8834>',
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
