from django.core.management.base import BaseCommand

from modules.config import config
from modules.translator import Translator

from sunless_web.models import Entity

from tqdm import tqdm
from modules.papago import papago


class Command(BaseCommand):

    def handle(self, *args, **options):
        translate_count = 0
        error_count = 0

        translator = Translator(config['key'], config['sheetId'])
        translator.load_noun()

        for entity in tqdm(Entity.objects.all()):
            if not entity.papago:
                papagos = {}

                for k, v in entity.original.items():
                    if k in ('parentName', 'Id') or not v:
                        continue

                    encoded = translator.encode_nouns(v)
                    transed = papago(encoded)

                    decoded = translator.decode_nouns(transed)
                    papagos[k] = decoded
                    print("")
                    translate_count += 1

                entity.papago = papagos
                entity.save()

        print("succ", translate_count, "err", error_count)
