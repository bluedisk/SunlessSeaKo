import re

from django.core.management.base import BaseCommand
from sunless_web.models import Entity, Noun, NounCate
from tqdm import tqdm
from .make_patch import get_nouns


def get_nouns():
    nouns = {}
    for noun in Noun.objects.all():
        key = "%s:%s" % (noun.cate.name, noun.pk)

        if noun.final:
            nouns[key] = (noun.name, noun.final)
        elif noun.translate:
            nouns[key] = (noun.name, noun.translate)
        elif noun.papago:
            nouns[key] = (noun.name, noun.papago)
        elif noun.google:
            nouns[key] = (noun.name, noun.google)
        else:
            nouns[key] = (noun.name, noun.name)

    return nouns


class Command(BaseCommand):

    def handle(self, *args, **options):
        nouns = get_nouns()
        en_dict = dict([(v[0], (re.compile(re.escape(v[0]), flags=re.IGNORECASE), "@[%s](%s)" % (v[0], k))) for k, v in nouns.items()])
        ko_dict = dict([(v[1], (re.compile(re.escape(v[0]), flags=re.IGNORECASE), "@[%s](%s)" % (v[0], k))) for k, v in nouns.items()])

        nidah = re.compile('(답|됩|입|읍|습|합)@\[Nidah\]\(지형:373\)')
        duplicate = re.compile('(?:@\[)+(@\[.+?\]\(\w+:\d+\))(?:\]\(\w+:\d+\))+')

        for e in tqdm(Entity.objects.all()):
            # @[A Gift for the Wistful Deviless](아이템:10)

            updated = False

            for field in ['Name', 'Teaser', 'Description']:
                if e.original.get(field, None):
                    updated = True
                    before = e.marked[field]
                    after = e.original[field]

                    for word, (comp, mark) in en_dict.items():
                        after = comp.sub(mark, after)

                    if before != after:
                        e.marked[field] = after
                        updated = True

                for trans_type in ['papago', 'google', 'translate', 'final']:
                    if getattr(e, trans_type).get(field, None):
                        before = getattr(e, trans_type)[field]
                        after = before
                        for word, (comp, mark) in ko_dict.items():
                            after = comp.sub(mark, after)
                            after = after.replace(word, mark)

                            if mark == "@[Nidah](지형:373)":
                                after = duplicate.sub('\g<1>', after)
                                after = after.replace('@[Nidah](지형:373).', '니다.')
                                after = nidah.sub('\g<1>니다.', after)

                        after = duplicate.sub('\g<1>', after)
                        if before != after:
                            getattr(e, trans_type)[field] = after
                            updated = True

            if updated:
                e.save()
