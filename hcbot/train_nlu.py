# -*- coding:utf-8 -*-

import botpath
import shutil

def train_nlu():
    print("=> Importing rasa_nlu...")
    from rasa_nlu.training_data import load_data
    from rasa_nlu import config
    from rasa_nlu.model import Trainer

    print("=> Training NLU...")
    training_data = load_data(botpath.NLU_DATA_FILE)
    trainer = Trainer(config.load(botpath.CONFIG_FILE))
    trainer.train(training_data)

    print("=> Saving Result...")
    shutil.rmtree(botpath.NLU_MODEL_PATH)
    model_directory = trainer.persist(botpath.NLU_MODEL_PATH, fixed_model_name=botpath.PROJECT)


if __name__ == '__main__':
    train_nlu()
