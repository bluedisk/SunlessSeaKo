"""
rest_entiries_by_entities 커맨드용 클래스 파일
"""
from django.core.management.base import BaseCommand
from django.db import transaction

import tqdm

from sunless_web.models import Entry, Entity, Translation, Discussion


class Command(BaseCommand):
    """ V1 > V2 데이터 마이그레이션용 임시 커맨드  """

    help = 'Delete all translations of entries and get from entities'

    @transaction.atomic
    def handle(self, *args, **options):

        Translation.objects.all().delete()
        Discussion.objects.all().delete()

        for entity in tqdm.tqdm(Entity.objects.all()):

            for field in ['Name', 'Teaser', 'Description']:
                original = entity.original.get(field, '')
                reference = entity.reference.get(field, '')
                papago = entity.papago.get(field, '')
                translate = entity.translate.get(field, '')
                final = entity.final.get(field, '')

                if original and (reference or papago or translate or final):
                    try:
                        entry = Entry.objects.get(hash_v1=entity.hash, object=field)

                        if not entry.checker.exists():
                            insert_as_checker(None, entry, translate, final)

                        for checker in entry.checker.all():
                            insert_as_checker(checker, entry, translate, final)

                        if reference:
                            entry.reference = reference

                        if papago:
                            entry.text_pp = papago

                        entry.update_status()
                        entry.save()

                    except Entry.DoesNotExist:
                        print(entity.hash, field, entity.path())
                        print("|".join([reference, papago, translate, final]))
                        raise ValueError()


def insert_as_checker(user, entry, translate, final):
    """ insert old tranlations to entry as user """

    if translate:
        trans = Translation(entry=entry, text=translate, user=user)
        trans.save()
        Discussion(msg='기존 유저 번역 등록', translate=trans).save()

    if final:
        trans = Translation(entry=entry, text=final, user=user)
        trans.save()
        Discussion(msg='기존 유저 번역 등록', translate=trans).save()
