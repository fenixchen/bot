# -*- coding:utf-8 -*-
import botpath

if __name__ == '__main__':
    print("=> Importing tensorflow...")
    import tensorflow as tf

    tf.logging.set_verbosity(tf.logging.ERROR)

    print("=> Importing rasa_nlu...")
    from rasa_core.interpreter import RasaNLUInterpreter
    from rasa_core.agent import Agent
    from rasa_core.policies.memoization import MemoizationPolicy
    from rasa_core.policies.keras_policy import KerasPolicy
    from rasa_core.channels.console import ConsoleInputChannel

    domain_file = botpath.DOMAIN_FILE

    interpreter = RasaNLUInterpreter(botpath.NLU_DATA_FOLDER)
    agent = Agent(domain_file,
                  policies=[MemoizationPolicy(max_history=3),
                            KerasPolicy()],
                  interpreter=interpreter)

    input_channel = ConsoleInputChannel()

    training_data = agent.load_data(botpath.STORY_FILE)
    agent.train_online(training_data,
                       input_channel=input_channel,
                       batch_size=50,
                       epochs=200,
                       max_training_samples=300)
