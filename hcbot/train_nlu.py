# -*- coding:utf-8 -*-

import botpath
import shutil
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="[%(filename)s:%(lineno)s] %(name)s - %(levelname)s - %(message)s")


def train_nlu():
    print("=> Importing rasa_nlu...")
    from rasa_nlu.training_data import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer
    shutil.rmtree(botpath.NLU_MODEL_PATH, ignore_errors=True)

    print("=> Training NLU...%s - %s" % (botpath.NLU_DATA_FILE, botpath.CONFIG_FILE))
    training_data = load_data(botpath.NLU_DATA_FILE)
    train_config = config.load(botpath.CONFIG_FILE)
    trainer = Trainer(train_config, skip_validation = True)
    trainer.train(training_data)

    print("=> Saving Result...%s" % botpath.NLU_MODEL_PATH)
    trainer.persist(botpath.NLU_MODEL_PATH, fixed_model_name=botpath.PROJECT)


if __name__ == '__main__':
    train_nlu()
