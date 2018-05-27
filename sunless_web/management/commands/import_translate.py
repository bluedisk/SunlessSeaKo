import codecs

from django.core.management.base import BaseCommand
from modules.sunless import RecursiveProcessor

from sunless_web.models import EntityCate, Entity

import re
import os
import json
import hgtk

from hashlib import sha256
from tqdm import tqdm


class Flatter(RecursiveProcessor):

    def __init__(self):
        super(Flatter, self).__init__()
        self.result_dict = {}

    def process(self, root):
        self.result_dict = {}
        succ, failed = super(Flatter, self).process(root)
        print("succ", succ, "failed", failed)
        return self.result_dict

    def _process_node(self, node, parentName):
        node_id = node['Id']

        if node_id in self.result_dict:
            self.result_dict[node_id].append(
                {
                    'parentName': parentName,
                    'Id': node['Id'],
                    'Name': node.get('Name', None),
                    'Teaser': node.get('Teaser', None),
                    'Description': node.get('Description', None)
                }
            )

        else:
            self.result_dict[node_id] = [{
                'parentName': parentName,
                'Id': node['Id'],
                'Name': node.get('Name', None),
                'Teaser': node.get('Teaser', None),
                'Description': node.get('Description', None)
            }]

        return True


class Command(BaseCommand):
    help = 'Update DB from translated json'

    def add_arguments(self, parser):
        parser.add_argument('source', nargs=1, type=str)
        parser.add_argument('category', nargs='?', type=str)

    def handle(self, *args, **options):
        flatter = Flatter()

        from pprint import pprint
        pprint(args)
        pprint(options)

        filename = options['source'][0]
        source_base = os.path.basename(filename)
        source_cate, _ = os.path.splitext(source_base)

        cate = options['category'] or source_cate
        print("Importing from %s to %s category" % (filename, cate))

        values = json.load(codecs.open(filename, encoding='utf-8-sig'))

        flat_origin = flatter.process(values)
        ef, _ = EntityCate.objects.get_or_create(name=cate)

        for key, entities in tqdm(flat_origin.items(), cate):
            for entity in entities:
                hash_key = Entity.make_hash(cate, entity['parentName'], key)

                try:
                    e = Entity.objects.get(hash=hash_key)
                    updated = False
                    for ek, val in entity.items():
                        if ek == 'Id':
                            continue

                        if val:
                            updated = True
                            if not hgtk.checker.is_latin1(val):
                                e.final[ek] = val.strip()
                            else:
                                e.final[ek] = ''

                    if updated:
                        e.save()
                except Exception as ex:
                    pprint(entity)
                    print(hash_key)
                    raise ex
