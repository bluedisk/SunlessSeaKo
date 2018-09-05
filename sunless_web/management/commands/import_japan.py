from django.core.management.base import BaseCommand
from sunless_web.models import EntityCate, Entry, Entity

import pickle
import os

from tqdm import tqdm


class Command(BaseCommand):
    help = 'Import translation from japan friends'

    def handle(self, *args, **options):

        with open(os.path.join(os.getcwd(), 'data/from_japan/translated.pkl'), "rb") as f:
            translated = pickle.load(f)

        with open(os.path.join(os.getcwd(), 'data/from_japan/hash_map.pkl'), "rb") as f:
            hash_map = pickle.load(f)

        for key, trans in tqdm(translated.items()):
            e, _ = Entry.objects.get_or_create(hash_v2=key)
            e.path = "/".join(trans['tree'])

            cate, _ = EntityCate.objects.get_or_create(name=trans['tree'][0])
            e.cate = cate

            e.hash_v1 = hash_map['downgrade'].get(key, None)
            e.hash_v2 = key

            e.text_en = trans['text'].get('en', None)
            e.text_jp = trans['text'].get('jp', None)
            e.text_jpkr = trans['text'].get('jp-kr', None)

            if e.text_jp:
                e.text_jp = e.text_jp.replace('\x00', ' ')

            if e.text_jpkr:
                e.text_jpkr = e.text_jpkr.replace('\x00', ' ')

            e.save()

            for oe in Entity.objects.filter(hash=e.hash_v1):
                for u in oe.checker.all():
                    e.checker.add(u)

            e.save()
