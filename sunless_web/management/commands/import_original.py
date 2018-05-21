from django.core.management.base import BaseCommand
from modules.sunless import RecursiveProcessor

from sunless_web.models import EntityFile, Entity

import re
import os
import json

from hashlib import sha256
from tqdm import tqdm

SHEET_ORIGINAL_PATH = "data/entities"
SHEET_VALUE_CATES = [
    #'areas_import',
    'areas',
    #'exchanges_import',
    'exchanges',
    #'personas_import',
    'personas',
    #'qualities_import',
    'qualities',
    # 'events_import',
    'events',
]


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
    help = 'Update from dumped json to DB'

    def handle(self, *args, **options):
        letter = re.compile('[^a-zA-Z]')
        flatter = Flatter()

        for cate in tqdm(SHEET_VALUE_CATES):
            with open(os.path.join(SHEET_ORIGINAL_PATH, "%s.json" % cate)) as f:
                values = json.load(f)

            flat_origin = flatter.process(values)
            ef, _ = EntityFile.objects.get_or_create(filename=cate)

            for key, entities in tqdm(flat_origin.items(), cate):
                for entity in entities:
                    key_string = "%s-%s" % (key, letter.sub('', str(entity['Name'])))
                    hash_key = sha256(key_string.encode('utf8')).hexdigest()

                    try:
                        Entity.objects.update_or_create(
                            hash=hash_key, defaults={
                                "file": ef,
                                "key": key,
                                "parent": entity['parentName'],
                                "original": entity
                            }
                        )
                    except Exception as e:
                        print(ef.filename)
                        print(key)
                        print(key_string)
                        print(hash_key)
                        print(json.dumps(entity))

                        raise e
