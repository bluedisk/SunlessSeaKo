###
### DEPRECATED
###

import json
import os
from pprint import pprint

from django.core.management.base import BaseCommand
from tqdm import tqdm

from modules.config import config
from modules.translator import Translator
from sunless_web.models import EntityCate, Entity, Noun, NounCate

SHEET_DOWNLOAD_PATH = "data/sheets"
SHEETS = {
    'areas': [],
    'exchanges': [],
    'personas': [],
    'qualities': [
        'qualities.json'
    ],
    'events': [
        'events1.json',
        'events2.json',
        'events3.json'
    ]
}


def update_translations(cate, values):
    updated_row = []
    errored_row = []

    ef = EntityCate.objects.get(cate)

    for key, trans in tqdm(values.items(), cate):
        matched_entities = Entity.objects.filter(file=ef, key=int(key))
        if not matched_entities:
            print("\n!!!!!!! no key !!!!!!!!! [%s]" % key)
            errored_row.append(key)
            continue

        for tran in trans:
            matched = 0

            name = tran['origin'].get('Name', '')
            dotname = "'" + name

            for entity in matched_entities:
                if entity.original['Name'] == name or entity.original['Name'] == dotname:
                    matched += 1

                    updated = False
                    for target in ('google', 'reference', 'translate', 'final'):
                        if getattr(entity, target) != tran[target]:
                            setattr(entity, target, tran[target])
                            updated = True

                    if updated:
                        updated_row.append(entity.id)
                        entity.save()

            if matched == 0:
                print(key, "\n!!!!not founded in entities!!!!!!!!")
                errored_row.append(key)

                print("origin:", name)
                for entity in matched_entities:
                    print("db    ==>", entity.original['Name'])

                for val in trans:
                    print("vals ==>", val['origin']['Name'])

            elif matched > 1:
                errored_row.append(key)
                print(key, "\n!!!!too many matched!!!!!!!!!!")

    return updated_row, errored_row


class Command(BaseCommand):
    help = 'Download all sheet data from google'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-download',
            action='store_true',
            dest='no-download',
            help="Don't Download and Using Saved data",
        )

    def handle(self, *args, **options):
        translator = Translator(config['key'], config['sheetId'])

        if not options['no-download']:
            # download noun
            translator.load_noun()
            translator.save_noun(os.path.join(SHEET_DOWNLOAD_PATH, "nouns.json"))

            # update noun db
            for key, noun_info in tqdm(translator.nouns().items(), 'update nouns'):
                cate, _ = NounCate.objects.get_or_create(name=noun_info['cate'])
                noun, _ = Noun.objects.get_or_create(name=noun_info['origin'], defaults={"cate": cate})

                updated = False
                for field in ['reference', 'google', 'translate', 'final']:
                    if getattr(noun, field) != noun_info[field]:
                        updated = True
                        setattr(noun, field, noun_info[field])

                if updated:
                    noun.save()

            # download sheets
            for cate, sheet_names in SHEETS.items():
                values = {}
                print("Downloading for %s" % cate)

                for idx, sheet_name in enumerate(sheet_names):
                    print("    Loading '%s' %d/%d" % (sheet_name, idx + 1, len(sheet_names)))
                    values.update(translator.load_all(sheet_name))

                with open(os.path.join(SHEET_DOWNLOAD_PATH, "%s.json" % cate), 'w') as f:
                    json.dump(values, f)

        else:
            translator.load_noun(os.path.join(SHEET_DOWNLOAD_PATH, "nouns.json"))

        # processing
        for cate, sheet_names in SHEETS.items():
            print("Processing for %s" % cate)

            trans_filename = os.path.join(SHEET_DOWNLOAD_PATH, "%s.json" % cate)

            if os.path.exists(trans_filename):
                with open(trans_filename) as f:
                    values = json.load(f)

                updated, errored = update_translations(cate, values)

                print("%s updates %s items" % (cate, len(updated)))
                pprint(errored)

            else:
                print("%s updates 0", cate)
