import re

from django.db.models.functions import Length
from django.core.management.base import BaseCommand
from sunless_web.models import Entity, Noun, NounCate
from tqdm import tqdm
from .make_patch import get_nouns


def get_nouns():
    nouns = []
    for noun in Noun.objects.all().order_by(Length('name').desc()):
        key = noun.pk

        if noun.final:
            nouns.append((key, noun.name, noun.final))
        elif noun.translate:
            nouns.append((key, noun.name, noun.translate))
        elif noun.papago:
            nouns.append((key, noun.name, noun.papago))
        elif noun.google:
            nouns.append((key, noun.name, noun.google))
        else:
            nouns.append((key, noun.name, noun.name))

    return nouns


class Command(BaseCommand):

    def handle(self, *args, **options):
        nouns = get_nouns()
        word_list = [(en, kr, re.compile(r'\b%s(?:\b|([^a-zA-Z0-9\s]+))' % re.escape(en), flags=re.IGNORECASE), "!N%04d!" % k) for k, en, kr in nouns]

        wrong_nidah1 = re.compile(r'(답|됩|듭|입|읍|습|합|줍|옵|랍|립|킵)'+re.escape('!N0373!'))
        wrong_nidah2 = re.compile(re.escape('!N0373!')+r'(\.|\!|"|\')')
        #duplicate = re.compile('(?:@\[)+(@\[.+?\]\(\w*:\d+\))(?:\]\(\w*:\d+\))+')

        for e in tqdm(Entity.objects.all()):
            # @[A Gift for the Wistful Deviless](아이템:10)
            updated = False

            for field in ['Name', 'Teaser', 'Description']:
                if e.original.get(field, None):
                    updated = True
                    before = e.marked.get(field, e.original[field])
                    after = e.original[field]

                    for _, _, regex, key in word_list:
                        after = regex.sub(key + "\g<1>", after)

                    if before != after:
                        e.marked[field] = after
                        updated = True

                for trans_type in ['papago', 'google', 'translate', 'final']:
                    if getattr(e, trans_type).get(field, None):
                        before = getattr(e, trans_type)[field]
                        after = before
                        for _, kr, regex, key in word_list:
                            after = regex.sub(key + "\g<1>", after)  # 영문
                            after = after.replace(kr, key)  # 한글

                            # 이게 문제입nidah... ㅠㅜ
                            if key == "!N0373!":
                                after = wrong_nidah1.sub('\g<1>니다', after)
                                after = wrong_nidah2.sub('니다\g<1>', after)

                        if before != after:
                            getattr(e, trans_type)[field] = after
                            updated = True

            if updated:
                e.save()
