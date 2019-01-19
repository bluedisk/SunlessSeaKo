"""
utilities for make fetch or extract data from json
"""
import re
from abc import ABCMeta, abstractmethod

import hgtk

from sunless_web.models import Entity, Entry

EXCLUDE_OBJECTS = (
    # events
    'LinkToEvent', 'Deck', 'LimitedToArea',
    'QualitiesAffected', 'QualitiesRequired',
    'Setting', 'SwitchToSetting',

    # exchange
    'Availabilities',

    # qualities
    'AssignToSlot',
    'AssociatedQuality',
    'UseEvent',
)


class RecursiveProcessor(metaclass=ABCMeta):
    """ 계층적인 구조의 데이터 처리를 위한 프로세서"""
    def __init__(self):
        self.processed = 0
        self.notprocessed = 0

    @abstractmethod
    def process(self, root, *args, **kwargs):
        """ 처리 시작점 """
        self.processed = 0
        self.notprocessed = 0

        self._recusive_process(root, 'root')

        return self.processed, self.notprocessed

    @abstractmethod
    def _process_node(self, node, parent):
        """ 실제 데이터 처리 부 """
        return False

    def _recusive_process(self, node, parent):
        if isinstance(node, dict):
            if node.get('Id', None) and (
                    (node.get('Name', None) and node['Name'].strip()) or
                    (node.get('Teaser', None) and node['Teaser'].strip()) or
                    (node.get('Description', None) and node['Description'].strip())
            ):
                if self._process_node(node, parent):
                    self.processed += 1
                else:
                    self.notprocessed += 1

            for key, value in node.items():
                if key not in EXCLUDE_OBJECTS:
                    self._recusive_process(value, key)

        elif isinstance(node, list):
            for item in node:
                self._recusive_process(item, parent)


class RecursiveUpdateProcessor(RecursiveProcessor):
    """ 데이터 업데이트를 위한 프로세서 """

    def __init__(self):
        super(RecursiveUpdateProcessor, self).__init__()
        self.trans_dict = {}
        self.nouns_dict = {}
        self.cate = ''
        self.noun_format = re.compile(r'(.*?)!N(\d{4})!(.*?)')
        self.left_word = re.compile(r"[\w']+")

    def get_best_trans(self, trans, field):
        if trans['final'].get(field, None):
            best = trans['final'][field]
        elif trans['translate'].get(field, None):
            best = trans['translate'][field]
        elif trans['papago'].get(field, None):
            best = "P: " + trans['papago'][field]
        elif trans['google'].get(field, None):
            best = "G: " + trans['google'][field]
        else:
            best = trans['original'][field]

        def make_noun_text(x):
            pre, id, post = x.groups()
            lefted_first = self.left_word.findall(post)

            if lefted_first:
                josa_type = hgtk.josa.get_josa_type(lefted_first[0])
            else:
                josa_type = None

            word = self.nouns_dict[int(id)][1]

            if josa_type:
                nexts = " ".join(lefted_first[1:])
                word = hgtk.josa.attach(word, josa_type)
                return pre + word + nexts
            else:
                return pre + word + post

        return self.noun_format.sub(make_noun_text, best)

    def process(self, cate, root, trans_dict, nouns_dict, *args, **kwargs):
        self.cate = cate
        self.trans_dict = trans_dict
        self.nouns_dict = nouns_dict
        return super(RecursiveUpdateProcessor, self).process(root, *args, **kwargs)

    def _process_node(self, node, parent):
        key = Entry.make_hash(self.cate, parent, node['Id'])
        trans = self.trans_dict.get(key, None)
        if not trans:
            print("Not matched hash", key, self.cate, parent, node['Id'])
            return False

        for field in ['Name', 'Teaser']:
            if trans['original'].get(field, None):
                node[field] = self.get_best_trans(trans, field)

        for field in ['Description']:
            if trans['original'].get(field, None):
                node[field] = "\r\n" + self.get_best_trans(trans, field)

        if 'Teaser' in node and not trans.get('Teaser', None) and trans.get('Description', None):
            teaser_filler = trans['Description'].split('.')[0][:30]
            node['Teaser'] = teaser_filler

        return True
