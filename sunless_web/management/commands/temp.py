import re

from django.core.management.base import BaseCommand
from sunless_web.models import Entity
from tqdm import tqdm


class Command(BaseCommand):

    def handle(self, *args, **options):
        saved = 0
        duplicate = re.compile('(?:@\[)+(@\[.+?\]\(\w+:\d+\))')

        for e in tqdm(Entity.objects.all()):
            updated=False
            for trans_type in ['papago', 'google', 'translate', 'final']:
                for field in ['Name', 'Teaser', 'Description']:
                    if getattr(e, trans_type).get(field, None):
                        updated = True
                        getattr(e, trans_type)[field] = duplicate.sub('\g<1>', getattr(e, trans_type)[field])
            if updated:
                saved += 1
                e.save()

        print("Total", saved, "saved.")
