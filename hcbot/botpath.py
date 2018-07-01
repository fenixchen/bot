# -*- coding:utf-8 -*-

PROJECT = "simple"

DATA_FOLDER = PROJECT + '/'

CONFIG_FILE = DATA_FOLDER + "config.yml"

NLU_DATA_FILE = DATA_FOLDER + "data.json"

DOMAIN_FILE = DATA_FOLDER + 'domain.yml'

STORY_FILE = DATA_FOLDER + 'stories.md'

NLU_MODEL_PATH = "models/nlu/"

NLU_DATA_FOLDER = NLU_MODEL_PATH + "/default/" + PROJECT

DIALOGUE_PATH = "models/dialogue/" + PROJECT