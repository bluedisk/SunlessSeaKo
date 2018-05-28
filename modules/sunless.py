import hashlib
import re
import sys
from pprint import pprint

import hgtk

from sunless_web.models import Entity

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


class RecursiveProcessor:
    def __init__(self):
        self.processed = 0
        self.notprocessed = 0
        
    def process(self, root, *args, **kwargs):
        self.processed = 0
        self.notprocessed = 0
        
        self._recusive_process(root, 'root')
        
        return self.processed, self.notprocessed
    
    def _process_node(self, node, parent):
        return False

    def _recusive_process(self, node, parent):
        if type(node) == dict:
            if node.get('Id', None) and (
                    (node.get('Name', None) and node['Name'].strip()) or
                    (node.get('Teaser', None) and node['Teaser'].strip()) or
                    (node.get('Description', None) and node['Description'].strip())
            ):
                if self._process_node(node, parent):
                    self.processed += 1
                else:
                    self.notprocessed += 1

            for k, v in node.items():
                if k not in EXCLUDE_OBJECTS:
                    self._recusive_process(v, k)

        elif type(node) == list:
            for item in node:
                self._recusive_process(item, parent)


class RecursiveUpdateProcessor(RecursiveProcessor):

    def __init__(self):
        super(RecursiveUpdateProcessor, self).__init__()
        self.trans_dict = {}
        self.nouns_dict = {}
        self.cate = ''
        self.noun_format = re.compile('(.*?)@\[.+?\]\(.+?:(.+?)\)(.*?)')
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
            pre, id, post = x
            lefted_first = self.left_word.findall(post)
            josa_type = hgtk.josa.get_josa_type(lefted_first[0])

            word = self.nouns_dict[id]

            if josa_type:
                nexts = " ".join(lefted_first[1:])
                word = hgtk.josa.attach(word, josa_type)
                return post + word + nexts
            else:
                return post + word + post

        return self.noun_format.sub(make_noun_text, best)

    def process(self, cate, root, trans_dict, nouns_dict, *args, **kwargs):
        self.cate = cate
        self.trans_dict = trans_dict
        self.nouns_dict = nouns_dict
        return super(RecursiveUpdateProcessor, self).process(root, *args, **kwargs)

    def _process_node(self, node, parent):
        key = Entity.make_hash(self.cate, parent, node['Id'])
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

