from django.core.management.base import BaseCommand
from django.db import transaction

from sunless_web.models import EntityCate, Entry, Entity, Translation, Discussion

import pickle
import os

from tqdm import tqdm


class Command(BaseCommand):
    help = 'Delete all translations of entries and get from entities'

    @transaction.atomic
    def handle(self, *args, **options):

        Translation.objects.all().delete()
        Discussion.objects.all().delete()

        for entity in tqdm(Entity.objects.all()):

            for field in ['Name', 'Teaser', 'Description']:
                original = entity.original.get(field, '')
                reference = entity.reference.get(field, '')
                papago = entity.papago.get(field, '')
                translate = entity.translate.get(field, '')
                final = entity.final.get(field, '')

                if original and (reference or papago or translate or final):
                    try:
                        entry = Entry.objects.get(hash_v1=entity.hash, object=field)
                        if papago:
                            entry.text_pp = papago
                            entry.save()

                        if translate:
                            trans = Translation(entry=entry, text=translate)
                            trans.save()
                            Discussion(entry=entry, msg='기존 유저 번역 등록', translate=trans).save()

                        if final:
                            trans = Translation(entry=entry, text=final)
                            trans.save()
                            Discussion(entry=entry, msg='기존 유저 번역 등록', translate=trans).save()

                        if reference:
                            Discussion(entry=entry, msg=reference).save()

                    except Entry.DoesNotExist:
                        print(entity.hash, field, entity.path())
                        print("|".join([reference, papago, translate, final]))
                        raise ValueError()
