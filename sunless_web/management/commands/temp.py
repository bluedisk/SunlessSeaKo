import re

from django.core.management.base import BaseCommand
from sunless_web.models import Entity, Noun
from tqdm import tqdm


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
        saved = 0

        nouns = get_nouns()
        # en_dict = dict([(v[0], (re.compile(re.escape(v[0]), flags=re.IGNORECASE), "@[%s](%s)" % (v[0], k))) for k, v in nouns.items()])
        # ko_dict = dict([(v[1], (re.compile(re.escape(v[0]), flags=re.IGNORECASE), "@[%s](%s)" % (v[0], k))) for k, v in nouns.items()])

#         nidah = re.compile('(답|됩|듭|입|읍|습|합|줍|옵|랍|립|킵)@\[Nidah\]\(지형:373\)')
#         duplicate = re.compile('(?:@\[)+(@\[.+?\]\(\w*:\d+\))(?:\]\(\w*:\d+\))+')

        for e in tqdm(Entity.objects.all()):
            updated=False
            for trans_type in ['papago', 'google', 'translate', 'final']:
                for field in ['Name', 'Teaser', 'Description']:
                    if getattr(e, trans_type).get(field, None):
                        updated = True
                        for key, (noun_en, noun_kr) in nouns.items():
                            getattr(e, trans_type)[field] = getattr(e, trans_type)[field].replace(key, noun_en)

            if updated:
                saved += 1
                e.save()

        print("Total", saved, "saved.")
