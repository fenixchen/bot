# -*- coding:utf-8 -*-

import botpath
import shutil


def train_dlg():
    print("=> Importing tensorflow...")
    import tensorflow as tf
    tf.logging.set_verbosity(tf.logging.ERROR)

    print("=> Importing rasa...")
    from rasa_core.agent import Agent
    from rasa_core.policies.memoization import MemoizationPolicy
    from rasa_core.policies.keras_policy import KerasPolicy

    agent = Agent(botpath.DOMAIN_FILE,
                  policies=[MemoizationPolicy(max_history=3),
                            KerasPolicy()])

    print("Training dialogue %s" % botpath.STORY_FILE)

    training_data = agent.load_data(botpath.STORY_FILE)

    agent.train(
        training_data,
        epochs=200,
        batch_size=50,
        max_training_samples=300
    )
    print("=> Saving Result to %s..." % botpath.DIALOGUE_PATH)

    shutil.rmtree(botpath.DIALOGUE_PATH, ignore_errors=True)
    agent.persist(botpath.DIALOGUE_PATH)


if __name__ == '__main__':
    train_dlg()
