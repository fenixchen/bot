# -*- coding:utf-8 -*-
import yaml
import json
import re
import itertools
import train_nlu
import train_dlg
import os
import random
import botpath
import sys

# 每个set最多包含的项目
MAX_ELEMENTS_PER_SET = 100

# 单个Story最多包含的实例
MAX_INSTANCE_PER_STORY = 100

# 每个intent最多的例子
MAX_COMMON_EXAMPLES = 100


class NLUData(object):
    def __init__(self):
        self._sets = {}
        self._intents = []
        self._pre_defined_slots = {}
        self._templates = {}
        self._actions = {}
        self._stories = []
        self._nlu_file = None

    @property
    def sets(self):
        return self._sets

    @property
    def intents(self):
        return self._intents

    def find_intent(self, name):
        for intent in self._intents:
            if intent.name == name:
                return True
        return False

    def find_utter(self, utter):
        for action in self._actions:
            if utter in action:
                return True
        else:
            return False

    def load(self, nlu_file):
        self._nlu_file = nlu_file
        print('Load NLU Config:<%s>' % nlu_file)
        f = open(nlu_file, 'r', encoding='UTF-8')
        data = yaml.load(f)
        f.close()

        assert 'sets' in data and 'intents' in data
        for name, elements in data['sets'].items():
            self._sets[name] = Set(self, name, elements)

        for intent, pattern in data['intents'].items():
            self._intents.append(Intent(self, intent, pattern))

        if 'slots' in data:
            self._pre_defined_slots.update(data['slots'])

        if 'templates' in data:
            self._templates.update(data['templates'])

        if 'actions' in data:
            self._actions = data['actions']

        if 'stories' in data:
            for name, story in data['stories'].items():
                self._stories.append(Story(self, name, story))

    def gen_intent_file(self, filename):
        intents_dict = {}
        common_example = []

        for intent in self._intents:
            common_example += intent.intent_list(self._sets)

        intents_common = {'common_examples': common_example}
        intents_dict['rasa_nlu_data'] = intents_common

        print('Save to intent file:<%s>' % filename)
        f = open(filename, 'w', encoding='UTF-8')
        json.dump(intents_dict, f, ensure_ascii=False, indent=2)
        f.close()

    def gen_domain_file(self, filename):
        slots = {}
        for intent in self._intents:
            slots.update(intent.slots())
        slots.update(self._pre_defined_slots)

        intent_list = []
        for intent in self._intents:
            intent_list.append(intent.name)

        entity_list = []
        for slot in slots:
            entity_list.append(slot)
        print('Save to domain file:<%s>' % filename)
        f = open(filename, 'w', encoding='UTF-8')
        f.write("slots:\n")
        for slot in slots:
            f.write('  %s:\n' % slot)
            f.write('    type: text\n')

        f.write("\nintents:\n")
        for intent in self._intents:
            f.write('  - %s\n' % intent.name)

        f.write('\nentities:\n')
        for slot in slots:
            f.write('  - %s\n' % slot)

        f.write('\ntemplates:\n')
        for action in self._actions:
            if type(action) is dict:
                name = next(iter(action))
                f.write('  %s:\n' % name)
                if name in action:
                    for t in action[name]:
                        f.write('    - \"%s\"\n' % t)

        f.write('\nactions:\n')
        for action in self._actions:
            if type(action) is dict:
                name = next(iter(action))
            else:
                name = action
            f.write('  - %s\n' % name)

        f.close()

    def gen_story_file(self, filename):
        content = ''
        for story in self._stories:
            if not story.check():
                break

        for story in self._stories:
            content += story.generate()
        print('Save to story file:<%s>' % filename)
        f = open(filename, 'w', encoding='UTF-8')
        f.write(content)
        f.close()

    def intent_sets(self, name):
        for intent in self._intents:
            if intent.name == name:
                return intent.intent_sets()
        assert False, "找不到intent <%s>" % name

    def load_file(self, file):
        fn = os.path.dirname(self._nlu_file) + '/' + file
        with open(fn, 'r', encoding='utf-8') as f:
            return f.read()
        assert (False)


class Story(object):
    INDEX = 0

    def __init__(self, nlu, name, steps):
        self._nlu = nlu
        self._name = name
        self._steps = steps

    def check(self):
        for step in self._steps:
            intent = next(iter(step))
            utters = step[intent]
            if not self._nlu.find_intent(intent):
                raise Exception("Cannot find intent %s" % intent)
            for utter in utters:
                if not self._nlu.find_utter(utter):
                    raise Exception("Cannot find utter %s" % utter)
        return True

    def generate(self):
        parts = []
        vector = []
        for step in self._steps:
            name = next(iter(step))
            sets = self._nlu.intent_sets(name)
            if len(sets) >= 1:
                count = 1
                vars = []
                for set in sets:
                    var = self._nlu.sets[set]
                    vars.append(var)
                    count *= var.count
                vector.append(list(range(0, count)))
                parts.append(vars)
            else:
                vector.append([0])
                parts.append(name)

        s = ''
        # 计算出所有组合的笛卡尔乘积, 产生[[0, 1, 0], [1, 2, 3], ...]
        # 每个列表代表一个story, 数字代表使用所在set的第几个
        count = 0
        product = list(list(itertools.product(*vector)))
        for v in product:
            s += '## story_%s_%d\n' % (self._name, Story.INDEX)
            Story.INDEX += 1
            for i, step in enumerate(self._steps):
                name = next(iter(step))
                utters = step[name]
                if type(parts[i]) == str:
                    s += '* %s\n' % name
                else:
                    s += '* %s{' % name
                    slots = {}
                    for part in parts[i]:
                        elem = part.elements[random.randint(0, part.count - 1)]
                        slots[part.name] = elem
                    for slot, value in slots.items():
                        s += '\"%s\": \"%s\",' % (slot, value)
                    s = s[:-2]
                    s += '}\n'
                    for slot, value in slots.items():
                        s += '    - slot{\"%s\": \"%s\"}\n' % (slot, value)
                for utter in utters:
                    s += '    - %s\n' % utter
                    if utter == 'action.ActionQueryInsurance':
                        s += '    - slot{"fee": 5000}\n'
            s += '\n'
            count += 1
            if count > MAX_INSTANCE_PER_STORY:
                break
        return s


class Set(object):
    def __init__(self, nlu, name, elements):
        self._nlu = nlu
        self._name = name
        self._elements = []
        for elem in elements:
            if type(elem) is dict:
                key, value = list(elem.items())[0]
                if key == 'file':
                    content = nlu.load_file(value)
                    lines = re.split('[\n \t,]+', content)
                    self._elements.extend(lines[:MAX_ELEMENTS_PER_SET])
                else:
                    assert False, 'Unknown key:' % key
            elif type(elem) is str:
                self._elements.append(elem)
            else:
                assert False, 'Unknown type:' % (type(elem))

    @property
    def name(self):
        return self._name

    @property
    def elements(self):
        return self._elements

    @property
    def count(self):
        return len(self._elements)

    def __str__(self):
        return 'Set(%s => %s)' % (self._name, self._elements)


class Intent(object):
    def __init__(self, nlu, name, patterns):
        self._nlu = nlu
        self._name = name
        self._patterns = patterns

    def __str__(self):
        return 'Intent(%s => %s)' % (self._name, self._patterns)

    @property
    def name(self):
        return self._name

    def intent_list(self, sets):
        intents = []
        for pattern in self._patterns:
            intents += self._generate_pattern(pattern)
        return intents

    def slots(self):
        slots = {}
        for pattern in self._patterns:
            for var in self._pattern_slots(pattern):
                slots[var] = {'type': 'text'}
        return slots

    # return [set1, set2]
    def intent_sets(self):
        sets = []
        for pattern in self._patterns:
            for var in self._pattern_slots(pattern):
                if var not in sets:
                    sets.append(var)
        return sets

    def _pattern_slots(self, pattern):
        slots = []
        sets = self._nlu.sets
        g = re.finditer(r'\$\(.*?\)', pattern)
        for m in list(g):
            match_start = m.start()
            match_end = m.end()
            var = pattern[match_start:match_end][2:-1]
            if var[0] == '_':
                continue
            assert var in sets, 'sets %s is not found' % var
            slots.append(var)

        return slots

    def _generate_pattern(self, pattern):
        sets = self._nlu.sets
        # [0]=>text or var name, [1]=>True: variable, False: Text, [2]: is a entity?
        spans = []

        start = 0
        g = re.finditer(r'\$\(.*?\)', pattern)
        for m in list(g):
            match_start = m.start()
            match_end = m.end()
            if match_start > start:
                spans.append([pattern[start:match_start], False, False])

            var = pattern[match_start:match_end][2:-1]
            if var[0] == '_':
                is_entity = False
                var = var[1:]
            else:
                is_entity = True

            assert var in sets, 'sets %s is not found' % var
            spans.append([var, True, is_entity])
            start = match_end

        if len(pattern) > start:
            spans.append([pattern[start:], False, False])

        return self._generate_span(spans)

    def _generate_span(self, spans):
        sets = self._nlu.sets
        intents = []
        vector = []
        for name, is_var, is_entity in spans:
            if is_var:
                vector.append(range(0, len(sets[name].elements)))
            else:
                vector.append([0])
        for v in list(itertools.product(*vector)):
            entities = []
            text = ''
            step = 0
            for name, is_var, is_entity in spans:
                start = len(text)
                if is_var:
                    t = sets[name].elements[v[step]]
                else:
                    t = name
                text += t
                end = start + len(t)
                if is_var and is_entity:
                    entities.append({
                        'start': start,
                        'end': end,
                        'value': t,
                        'entity': name,
                    })
                step += 1
            intents.append({
                'text': text,
                'intent': self._name,
                'entities': entities,
            })
            if len(intents) > MAX_COMMON_EXAMPLES:
                break
        return intents


yaml_file = botpath.PROJECT + '/' + botpath.PROJECT + '.nlu.yaml'

TRAIN_AFTER_GEN = False

if __name__ == '__main__':
    nlu_data = NLUData()
    nlu_data.load(yaml_file)
    nlu_data.gen_intent_file(botpath.NLU_DATA_FILE)
    nlu_data.gen_domain_file(botpath.DOMAIN_FILE)
    nlu_data.gen_story_file(botpath.STORY_FILE)
    for arg in sys.argv:
        if arg == '-g':
            TRAIN_AFTER_GEN = True
    if TRAIN_AFTER_GEN:
        train_nlu.train_nlu()
        train_dlg.train_dlg()
