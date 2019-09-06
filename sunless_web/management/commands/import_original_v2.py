"""
Make patch from V2 data(Entry)
"""
import re

from django.core.management.base import BaseCommand

from modules.papago import papago
from modules.sunless_v2 import run_all
from sunless_web.models import Entry, EntryPath, EntityCate, Translation, Discussion

missed = 0
updated = 0
not_changed = 0

BLACK_LIST = {
    'qualities': [
        re.compile(r'\d+/AssignToSlot'),
        re.compile(r'\d+/Enhancements'),
    ],
    'events': [
        re.compile(r'\d+/Deck'),
        re.compile(r'\d+/ChildBranches/\d+/DefaultEvent/MoveToArea'),
        re.compile(r'\d+/ChildBranches/\d+/SuccessEvent/MoveToArea'),
    ],
    'Tiles': [
        re.compile(r'\w+/Name'),
        re.compile(r'\w+/Tiles/[\w\d]+/Name'),
        re.compile(r'\w+/Tiles/[\w\d]+/SpawnPoints'),
        re.compile(r'\w+/Tiles/[\w\d]+/TerrainData'),
        re.compile(r'\w+/Tiles/[\w\d]+/PortData'),
        re.compile(r'\w+/Tiles/[\w\d]+/PhenomenaData'),

    ],
    'Associations': [
        re.compile(r'Associations/Name'),
    ],
    'SpawnedEntities': [
        re.compile(r'\w+/CombatItems'),
    ]
}


class Command(BaseCommand):
    """ 원본 데이터를 임포트해서 DB를 구축하는 import original 명령어를 핸들링 """
    help = 'Import Original DATA from Json V2'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', dest='dry-run', action='store_true')

    #     parser.add_argument('--force', dest='force', action='store_true')
    #     parser.add_argument('--print', dest='print', action='store_true')
    #     parser.add_argument('--save', dest='save', action='store_true')

    def handle(self, *args, **options):
        # make data

        def process_replace(hashkey, tree, value):
            global missed, not_changed, updated

            if not value or tree[-1] not in ('Name', 'HumanName', 'Description'):
                return value

            try:
                e = Entry.objects.get(hash_v2=hashkey)
                not_changed += 1

                if e.text_en != value:
                    updated += 1
                    if not options['dry-run']:
                        e.text_en = value
                        e.save()

                        for t in e.translations.all():
                            Discussion.objects.create(
                                translate=t,
                                msg='원문 업데이트 됨! 확인 필요합니다!'
                            )

            except Entry.DoesNotExist:
                missed += 1
                path = '/'.join(tree[1:])

                # print(tree[0], hashkey, path, value)
                cate = EntityCate.objects.get(name=tree[0])

                if not options['dry-run']:
                    epath, _ = EntryPath.objects.get_or_create(cate=cate, name=path)

                    Entry.objects.create(
                        path=epath,
                        basepath=path,
                        object=tree[-1],
                        hash_v2=hashkey,
                        text_en=value,
                        text_pp=papago(value)
                    )

            return value

        def can_go(tree):
            path = '/'.join(tree[1:])
            rules = BLACK_LIST.get(tree[0], [])

            for r in rules:
                if r.match(path):
                    return False

            return True

        run_all(process_replace, "data/original", can_go)

        print("no changed", not_changed)
        print("missed", missed)
        print("updated", updated)
