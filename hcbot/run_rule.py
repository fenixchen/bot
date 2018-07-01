# -*- coding:utf-8 -*-

import botpath


if __name__ == '__main__':
    print("=> Importing tensorflow...")
    import tensorflow as tf
    tf.logging.set_verbosity(tf.logging.ERROR)

    print("=> Importing rasa...")
    from rasa_core.interpreter import RasaNLUInterpreter
    from rasa_core.channels.console import ConsoleInputChannel
    from rasa_addons.superagent import SuperAgent

    print("=> HC NLU Bot Initializing...")
    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)
    agent = SuperAgent.load(botpath.DIALOGUE_PATH, interpreter=interpreter, rules_file="simple/rules.yml")

    agent.handle_channel(ConsoleInputChannel())
