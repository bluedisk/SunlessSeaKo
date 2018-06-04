import json
import sys
import zipfile

import os

import datetime
from io import BytesIO

from django.core.management.base import BaseCommand
from django.db.models import Q, Count, Sum
from django.utils import timezone

from modules.log import TelegramLog, PrintLog
from modules.sunless import RecursiveUpdateProcessor

from modules.config import config

from sunless_web.models import Patch, Entity, EntityCate, Noun, NounCate


################################################


def get_lastest_patch():
    return Patch.objects.order_by('-created_at').first()


def get_updated(check_from):
    noun_updated = Noun.objects.filter(updated_at__gt=check_from).count()
    entity_updated = Entity.objects.filter(updated_at__gt=check_from).values('cate').annotate(cnt=Count('cate'))

    return noun_updated, dict([(s['cate'], s['cnt']) for s in entity_updated])


def get_nouns():
    nouns = {}
    area_cate = NounCate.objects.get(name='지명, 지형')
    for noun in Noun.objects.all():
        if noun.cate == area_cate:
            addition = "(%s)" % noun.name
        else:
            addition = ''

        if noun.final:
            nouns[noun.pk] = (noun.name, noun.final + addition)
        elif noun.translate:
            nouns[noun.pk] = (noun.name, noun.translate + addition)
        elif noun.papago:
            nouns[noun.pk] = (noun.name, "P:" + noun.papago + addition)
        elif noun.google:
            nouns[noun.pk] = (noun.name, "G:" + noun.google + addition)
        else:
            nouns[noun.pk] = (noun.name, noun.name)

    return nouns


def make_patch(nouns_dict):
    trans_dict = {}
    cates = EntityCate.objects.all()

    for cate in cates:
        trans_dict[cate.name] = {}

    for e in Entity.objects.filter(cate__in=cates):
        trans_dict[e.cate.name][e.hash] = {
            'original': e.original or {},
            'google': e.google or {},
            'papago': e.papago or {},
            'translate': e.translate or {},
            'final': e.final or {}
        }

    # load original
    patches = {}
    for cate in cates:
        print("Creating %s ----" % cate.name)
        with open(os.path.join(config['path_original'], '%s.json' % cate.name), 'r') as f:
            patch = json.load(f)

        # # Replacing original text to translated
        updater = RecursiveUpdateProcessor()
        matched, unmatched = updater.process(cate.name, patch, trans_dict[cate.name], nouns_dict)
        print('matched:', matched, ', \tunmatched:', unmatched, " \t Percent: ", matched * 100 / (matched + unmatched), "%")

        patches[cate.name] = patch

    # Package files
    output_name = "sunless_sea_ko_%s.zip" % timezone.localtime().strftime('%Y%m%d')

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as myzip:
        for cate in EntityCate.objects.all():
            patch_text = json.dumps(patches[cate.name], ensure_ascii=False)
            myzip.writestr("%s.json" % cate.name, patch_text)

    # insert to DB
    patch = Patch()
    patch.items = Entity.objects.all().aggregate(cnt=Sum('items'))['cnt']
    patch.translated = Entity.objects.all().aggregate(cnt=Sum('translated'))['cnt']
    patch.finalized = Entity.objects.all().aggregate(cnt=Sum('finalized'))['cnt']
    patch.file.save(output_name, buffer, save=False)
    patch.save()

    return patch


class Command(BaseCommand):
    help = 'Make patch from DB'

    def add_arguments(self, parser):
        parser.add_argument('--force', dest='force', action='store_true')
        parser.add_argument('--print', dest='print', action='store_true')

    def handle(self, *args, **options):

        if options['print']:
            print("Log to console")
            log = PrintLog()
        else:
            print("Log to group %s" % config['botGroupId'])
            log = TelegramLog(config['botToken'], config['botGroupId'])

        log.log("""오늘도 좋은 하루! 썬리스 씨봇입니다! 
😛 오늘 버전 🇰🇷 패치 제작을 시작합니다! 
우우우웅~ 털털털!""")

        lastest = get_lastest_patch()
        if lastest:
            check_from = lastest.created_at
        else:
            check_from = timezone.make_aware(datetime.datetime(2018, 5, 26))

        noun_updated, entity_updated = get_updated(check_from)

        if not options['force'] and not noun_updated and not entity_updated:
            log.log("""⁉️ 지자스... 업데이트가 없습니다... 
따라서 오늘의 패치도 없습니다...😭""")
            sys.exit(0)

        updates = []
        if noun_updated:
            updates.append('명사 %s개' % noun_updated)

        for key, val in entity_updated.items():
            updates.append("%s에서 %s개" % (key, val))

        log.log("""오늘으으은~~! 
%s가 변경 되었습니다! 👍

🔊 처리를 시작합니다 지기지기~ 우우우웅~~ 둠칫둠칫~ 🔊
""" % ", ".join(updates))

        nouns = get_nouns()
        patch = make_patch(nouns)

        log.log("""

파일 생성 완료! 파일 다운로드는 아래 링크를 이용해 주세요!
--------------------------------------------
https://sunless.eggpang.net%s
""" % patch.get_absolute_url())

