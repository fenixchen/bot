# -*- coding:utf-8 -*-

import botpath

if __name__ == '__main__':
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

    agent.handle_channel(ConsoleInputChannel())
