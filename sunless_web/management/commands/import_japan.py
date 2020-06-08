import os
import pickle

from django.core.management.base import BaseCommand
from tqdm import tqdm

from sunless_web.models import Entry, Entity, EntryPath


class Command(BaseCommand):
    help = 'Import translation from japan friends'

    def handle(self, *args, **options):

        with open(os.path.join(os.getcwd(), 'data/from_japan/translated.pkl'), "rb") as f:
            translated = pickle.load(f)

        with open(os.path.join(os.getcwd(), 'data/from_japan/hash_map.pkl'), "rb") as f:
            hash_map = pickle.load(f)
        #
        # added = 0
        # for key, trans in tqdm(translated.items()):
        #     e, created = Entry.objects.get_or_create(hash_v2=key)
        #     if not created:
        #         continue
        #
        #     added = added + 1
        #
        #     fullpath = "/".join(trans['tree'])
        #
        #     e.object = os.path.basename(fullpath)
        #     e.basepath = fullpath[:fullpath.rindex("/")]
        #     e.path, _ = EntryPath.objects.get_or_create(name=e.basepath)
        #
        #     e.hash_v1 = hash_map['downgrade'].get(key, None)
        #     e.hash_v2 = key
        #
        #     e.text_en = trans['text'].get('en', None)
        #     e.text_jp = trans['text'].get('jp', None)
        #     e.text_jpkr = trans['text'].get('jp-kr', None)
        #
        #     if e.text_jp:
        #         e.text_jp = e.text_jp.replace('\x00', ' ')
        #
        #     if e.text_jpkr:
        #         e.text_jpkr = e.text_jpkr.replace('\x00', ' ')
        #
        #     e.save()
        #
        #     for oe in Entity.objects.filter(hash=e.hash_v1):
        #         for u in oe.checker.all():
        #             e.checker.add(u)
        #
        #     e.save()
        #
        # print("new data from japan", added)

        # import not translated data
        with open("data/from_japan/origin_eng.pkl", "rb") as f:
            origin_eng = pickle.load(f)

        added = 0
        for key, origin in tqdm(origin_eng.items()):
            if not origin['text']:
                continue

            e, created = Entry.objects.get_or_create(hash_v2=key)
            if not created:
                continue

            added = added + 1
            fullpath = "/".join(origin['tree'])

            if fullpath == "/":
                raise ValueError()

            e.object = os.path.basename(fullpath)
            e.basepath = fullpath[:fullpath.rindex("/")]
            e.path, _ = EntryPath.objects.get_or_create(name=e.basepath)

            e.hash_v1 = origin['hash_v1']
            e.hash_v2 = key

            e.text_en = origin['text']

            e.save()

            for oe in Entity.objects.filter(hash=e.hash_v1):
                for u in oe.checker.all():
                    e.checker.add(u)

            e.save()

        print("new data from origin", added)
