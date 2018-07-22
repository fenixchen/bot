# -*- coding:utf-8 -*-

import botpath
import logging
from termcolor import colored, cprint
import rasa_core

TEST_DIALOG = False



def run_interpreter():
    message = '车险'
    from rasa_core.interpreter import RasaNLUInterpreter
    print("=> HC NLU Bot Initializing...")
    print("Load NLU %s" % botpath.NLU_DATA_FOLDER)
    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)
    parse_data = interpreter.parse(message)
    print("Received user message '{}' with intent '{}' "
                 "and entities '{}'".format(message,
                                            parse_data["intent"],
                                            parse_data["entities"]))

def run():
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(filename)s:%(lineno)s] %(name)s - %(levelname)s - %(message)s")

    print("=> Importing tensorflow...")
    import tensorflow as tf
    tf.logging.set_verbosity(tf.logging.ERROR)

    print("=> Importing rasa...")
    from rasa_core.interpreter import RasaNLUInterpreter
    from rasa_core.channels.console import ConsoleInputChannel
    from rasa_core.agent import Agent

    print("=> HC NLU Bot Initializing...")
    print("Load NLU %s" % botpath.NLU_DATA_FOLDER)
    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)

    print("Load dialog %s" % botpath.DIALOGUE_PATH)
    agent = Agent.load(botpath.DIALOGUE_PATH, interpreter=interpreter)
    if TEST_DIALOG:
        agent.handle_channel(ConsoleInputChannel())
    else:
        rasa_core.policies.MemoizationPolicy.ENABLE_FEATURE_STRING_COMPRESSION = False
        index = 0
        dialogs = [
            ('车险', 'None\n'),
            ('你好', '欢迎致电世界500强平安,我是王伟,工号6500\n请问怎么称呼您\n'),
            ('我叫张三丰', '欢迎你, 张三丰\n请问您需要什么服务?\n'),
            ('车险', '请问你的车牌是什么?\n'),
            ('我的车牌是沪A12345', '您是平安的老客户了, 去年你投保的项目如下车损险,不计免赔,三责险100万, 车牌为沪牌, 总保费是5000元\n'
                             '请问确认要投保吗?\n'),
            ('确认', '张三丰, 您的车牌号为沪a12345的车投保已成功,保险费为5000,谢谢.\n'
                   '请问您需要什么服务?\n'),
        ]

        for question, expect in dialogs:
            cprint(("%d. " % index) + question, 'yellow')
            answers = agent.handle_message(question)
            answers_text = ''
            for msg in answers:
                if 'text' in msg:
                    answers_text += msg['text'] + '\n'
            if len(answers_text) == 0:
                answers_text = "No answer\n"
            cprint(("%d. " % index) + answers_text, 'green')
            if answers_text != expect:
                cprint(("测试失败, 期望:%s\n" % expect), 'red', attrs=['bold', 'blink'])
                break
            index += 1
        print("测试结束")


if __name__ == '__main__':
    run_interpreter()
    #run()
