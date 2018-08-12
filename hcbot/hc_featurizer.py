# -*- coding:utf-8 -*-
import yaml
import re
import os
from rasa_nlu.components import Component


class Set(object):
    def __init__(self, nlp, name, elements):
        self._nlp = nlp
        self._name = name
        self._elements = []
        for elem in elements:
            if type(elem) is dict:
                key, value = list(elem.items())[0]
                if key == 'file':
                    content = self.load_file(value)
                    lines = list(set(re.split('[\n \t,]+', content)))
                    self._elements.extend(lines)
                else:
                    assert False, 'Unknown key:' % key
            elif type(elem) is str:
                self._elements.append(elem)
            else:
                assert False, 'Unknown type:' % (type(elem))

    def load_file(self, file):
        file = self._nlp.curdir + '/' + file
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()
        assert False

    def to_regex(self):
        return '(' + '|'.join(self._elements) + ')'


class Intent(object):
    def __init__(self, nlp, name, patterns):
        self._nlp = nlp
        self._name = name
        self._patterns = patterns

    def to_match_items(self):
        start = 0
        sets = self._nlp.sets
        match_items = []
        for pattern in self._patterns:
            match_obj = re.fullmatch(r'\$\(.*?\)', pattern)
            if match_obj is not None:
                var = pattern[2:-1]
                if var[0] == '_':
                    var = var[1:]
                assert var in sets, 'sets %s is not found' % var
                match_items.append(HcMatchItem(sets[var].to_regex(), self._name, []))
            else:
                slots = []
                g = re.finditer(r'\$\(.*?\)', pattern)
                for m in list(g):
                    expr = ''
                    match_start = m.start()
                    match_end = m.end()
                    if match_start > start:
                        expr += pattern[start:match_start]
                    var = pattern[match_start:match_end][2:-1]
                    if var[0] == '_':
                        var = var[1:]
                    assert var in sets, 'sets %s is not found' % var
                    slots.append(var)
                    expr += '(.+)'
                match_items.append(HcMatchItem(expr, self._name, slots))
        return match_items


class HcMatchItem(object):
    def __init__(self, regex, intent, slots=[]):
        '''
        :param regex: str, regular expression
        :param intent:  str, intent name
        :param _slots: list, each slot name, ex: ['carno']
        '''
        self._regex = regex
        self._intent = intent
        self._slots = slots

    def match(self, text):
        '''
        :param text: input meesage
        :return: (intent, [entity]) # ex: ('inform_carno', [('carno': '沪F12345')]
        return (None, None) for unmatched
        '''
        # print('match %s-%s %s' % (self._intent, self._regex, text))
        match_objs = re.fullmatch(self._regex, text, re.IGNORECASE)
        if match_objs is None:
            return (None, None)
        else:
            entities = []
            group = 1
            for slot in self._slots:
                entity = {"entity": slot, "value": match_objs.group(group)}
                entities.append(entity)
            return self._intent, entities


class HcRegexNLP(Component):
    name = "nlp_hc"

    config_file = "mitie_test/mitie_test.nlu.yaml"

    defaults = {
    }

    def __init__(self, component_conf):
        super(HcRegexNLP, self).__init__(component_conf)
        print('Load HC RegEx Config:<%s>' % HcRegexNLP.config_file)
        f = open(HcRegexNLP.config_file, 'r', encoding='UTF-8')
        data = yaml.load(f)
        f.close()

        self._config_file = HcRegexNLP.config_file

        self._sets = {}

        self._match_list = []  # MatchItem

        assert 'sets' in data and 'intents' in data

        for name, elements in data['sets'].items():
            self._sets[name] = Set(self, name, elements)

        for intent, pattern in data['intents'].items():
            intent = Intent(self, intent, pattern)
            match_items = intent.to_match_items()
            self._match_list.extend(match_items)

    @property
    def sets(self):
        return self._sets

    @property
    def curdir(self):
        return os.path.dirname(self._config_file)

    @classmethod
    def cache_key(cls, model_metadata):
        return "hc_regex_featurizer"

    @classmethod
    def create(cls, cfg):
        component_conf = cfg.for_component(cls.name, cls.defaults)
        return HcRegexNLP(component_conf)

    def process(self, message, **kwargs):
        intent_dict = None
        entities_list = []
        for mi in self._match_list:
            intent, entities = mi.match(message.text)
            if intent is not None:
                intent_dict = {
                    'name': intent,
                    'confidence': 1.0
                }
                entities_list = entities
                break
        if intent_dict is not None:
            message.set('entities', entities_list, add_to_output=True)
            message.set('intent', intent_dict, add_to_output=True)


TEST_CASES = {
    '再见': 'intent<goodbye>',
    'bye': 'intent<goodbye>',
    '你好': 'intent<greet>',
    'hello': 'intent<greet>',
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

if __name__ == '__main__':
    '''
    match_objs = re.fullmatch('我是(.+)', '我是王二小', re.IGNORECASE)
    print(match_objs)
    '''
    from rasa_nlu.training_data.message import Message
    from termcolor import cprint

    nlp = HcRegexNLP(None)
    for text, expected in TEST_CASES.items():
        message = Message(text)
        nlp.process(message)
        if 'intent' in message.data:
            intent = message.data["intent"]
            entities = message.data["entities"]
            result = "intent<%s>" % intent['name']
            if len(entities) > 0:
                result += ' slot<'
                for entity in entities:
                    result += entity['entity'] + ':' + entity['value'] + ' '
                result = result[:-1] + '>'
        else:
            result = "intent<>"
        if result != expected:
            cprint("%s => %s failed" % (text, result), 'red')
        else:
            cprint("%s => %s success" % (text, result), 'green')
