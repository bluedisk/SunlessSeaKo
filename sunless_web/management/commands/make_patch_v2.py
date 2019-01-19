"""
Make patch from V2 data(Entry)
"""
import json
import re
import sys
import zipfile

import datetime
from io import BytesIO

import hgtk
import tqdm
from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.utils import timezone

from modules.log import TelegramLog, PrintLog
from modules.sunless import RecursiveUpdateProcessor

from modules.config import config
from modules.sunless_v2 import run_all

from sunless_web.models import Patch, EntityCate, Noun, NounCate, Entry


################################################


def get_lastest_patch():
    """ 마지막 생성된 패치 정보를 가져온다 """

    return Patch.objects.order_by('-created_at').first()


def get_updated(check_from):
    """ check_from 이후 업데이트된 정보 갯수를 가져온다 """

    noun_updated = Noun.objects.filter(updated_at__gt=check_from).count()
    entry_updated = Entry.objects.filter(updated_at__gt=check_from).values('path__cate').annotate(cnt=Count('path__cate'))

    return noun_updated, {e['path__cate']: e['cnt'] for e in entry_updated}


def get_nouns():
    """ 명사 번역 정보를 가져온다 """

    nouns = {}
    area_cate = NounCate.objects.get(name='지명, 지형')
    for noun in tqdm.tqdm(Noun.objects.all(), "Loading Nouns"):
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


def get_trans(nouns_dict, accept_jpkr, accept_auto):
    # compile regex
    noun_format = re.compile(r'(.*?)!N(\d{4})!(.*?)')
    left_format = re.compile(r"[\w']+")

    # noun replacer
    def make_noun_text(x):
        pre, id, post = x.groups()
        lefted_first = left_format.findall(post)

        if lefted_first:
            josa_type = hgtk.josa.get_josa_type(lefted_first[0])
        else:
            josa_type = None

        word = nouns_dict[int(id)][1]

        if josa_type:
            nexts = " ".join(lefted_first[1:])
            word = hgtk.josa.attach(word, josa_type)
            return pre + word + nexts
        else:
            return pre + word + post

    # load translations
    trans_dict = {}

    if not accept_jpkr and not accept_auto:
        entries = Entry.objects.annotate(tcount=Count('translations')).exclude(tcount=0)
    else:
        entries = Entry.objects.all()

    for entry in tqdm.tqdm(entries, 'Loading Translations'):
        entry_trans = entry.get_trans(accept_jpkr, accept_auto)
        if entry_trans:
            trans_dict[entry.hash_v2] = noun_format.sub(make_noun_text, entry_trans)

    return trans_dict


def make_patch(trans_dict):
    """ 한글 패치를 생성한다 """

    # make data
    def process_replace(hashkey, value):
        if hashkey in trans_dict:
            return trans_dict[hashkey].replace('\x00', ' ')

        return value

    fetch_data = run_all(process_replace, "data/original")

    # Package files
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as myzip:
        for fetch_file, fetch_json in fetch_data.items():
            patch_text = json.dumps(fetch_json, ensure_ascii=False)
            myzip.writestr(fetch_file, patch_text)

    return buffer


class Command(BaseCommand):
    """ 한글 패치를 생성하는 make_patch 명령어를 핸들링 """
    help = 'Make patch from DB V2'

    def add_arguments(self, parser):
        parser.add_argument('--pre-check', dest='pre-check', action='store_true')
        parser.add_argument('--force', dest='force', action='store_true')
        parser.add_argument('--print', dest='print', action='store_true')
        parser.add_argument('--save', dest='save', action='store_true')

    def handle(self, *args, **options):

        if options['print']:
            print("Log to console")
            log = PrintLog()
        else:
            print("Log to group %s" % config['botGroupId'])
            log = TelegramLog(config['botToken'], config['botGroupId'])

        if not options['pre-check']:
            log.log("오늘도 좋은 하루! 썬리스 씨봇입니다!\n 😛 오늘 버전 🇰🇷 패치 제작을 시작합니다!")

        lastest = get_lastest_patch()
        if lastest:
            check_from = lastest.created_at
        else:
            check_from = timezone.make_aware(datetime.datetime(2018, 5, 26))

        noun_updated, entity_updated = get_updated(check_from)

        if options['pre-check']:
            if not noun_updated and not entity_updated:
                log.log("아직 오늘 업데이트 된 내용이 없습니다! 🏰 깨어나세요 용사여! ⚔️ 힘을 모아주세요! 🥁")
                print("no update alert")
            else:
                print("updates %s - %s" % (noun_updated, entity_updated))

            sys.exit(0)

        if not options['force'] and not noun_updated and not entity_updated:
            log.log("""⁉️ 지자스... 업데이트가 없습니다... \n 따라서 오늘의 패치도 없습니다...😭""")
            sys.exit(0)

        updates = []
        if noun_updated:
            updates.append('명사 %s개' % noun_updated)

        for key, val in entity_updated.items():
            updates.append("%s에서 %s개" % (key, val))

        log.log("%s가 변경 되었습니다! 👍\n\n 🔊 처리를 시작합니다 지기지기~ 우우우웅~~ 둠칫둠칫~ 🔊\n " %
                ", ".join(updates))

        nouns = get_nouns()

        print("Make minimum version")
        trans = get_trans(nouns, False, False)
        min_patch_data = make_patch(trans)
        min_patch_data.seek(0)

        print("Make full version")
        trans = get_trans(nouns, True, True)
        full_patch_data = make_patch(trans)
        full_patch_data.seek(0)

        print("Save File or Update DB")
        if options['save']:
            patch_filename = "sunless_sea_ko_min_%s.zip" % timezone.localtime().strftime('%Y%m%d')
            with open(patch_filename, "wb+") as patch_file:
                patch_file.write(min_patch_data.getbuffer())

            log.log(""" 최소 파일 생성 완료! : %s""" % patch_filename)

            patch_filename = "sunless_sea_ko_full_%s.zip" % timezone.localtime().strftime('%Y%m%d')
            with open(patch_filename, "wb+") as patch_file:
                patch_file.write(full_patch_data.getbuffer())

            log.log(""" 전체 파일 생성 완료! : %s""" % patch_filename)

        else:
            # insert to DB
            min_patch = Patch()
            min_patch.patch_type = 'minimum'
            min_patch.items = Entry.objects.count()
            min_patch.translated = Entry.objects.filter(status='partial').count()
            min_patch.finalized = Entry.objects.filter(status='finished').count()
            min_patch.file.save("sunless_sea_ko_min_%s.zip" % timezone.localtime().strftime('%Y%m%d'), min_patch_data, save=False)
            min_patch.save()

            full_patch = Patch()
            full_patch.patch_type = 'full'
            full_patch.items = Entry.objects.count()
            full_patch.translated = Entry.objects.filter(status='partial').count()
            full_patch.finalized = Entry.objects.filter(status='finished').count()
            full_patch.file.save("sunless_sea_ko_full_%s.zip" % timezone.localtime().strftime('%Y%m%d'), full_patch_data, save=False)
            full_patch.save()

            log.log("""
    
    파일 생성 완료! 파일 다운로드는 아래 링크를 이용해 주세요!
    --------------------------------------------
    최소버전 : https://sunless.eggpang.net%s
    풀버전: https://sunless.eggpang.net%s""" % (min_patch.get_absolute_url(), full_patch.get_absolute_url()))
