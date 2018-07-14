# -*- coding:utf-8 -*-

import botpath
import logging

if __name__ == '__main__':
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
    # answers = agent.handle_message('你好')
    # print(answers)

    agent.handle_channel(ConsoleInputChannel())
