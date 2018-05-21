from django.core.management.base import BaseCommand

from modules.config import config
from modules.translator import Translator

from sunless_web.models import Entity

import json
import requests
from tqdm import tqdm

PAPAGO_ENDPOINT = 'https://naveropenapi.apigw.ntruss.com/nmt/v1/translation'


class Command(BaseCommand):

    def handle(self, *args, **options):
        translate_count = 0
        error_count = 0

        translator = Translator(config['key'], config['sheetId'])
        translator.load_noun()

        for entity in tqdm(Entity.objects.all()):
            if not entity.papago:
                papago = {}

                for k, v in entity.original.items():
                    if k in ('parentName', 'Id') or not v:
                        continue

                    encoded = translator.encode_nouns(v)
                    #print("")
                    #print("o", v)
                    #print("e", encoded)

                    res = requests.post(PAPAGO_ENDPOINT, data={
                            'source': 'en',
                            'target': 'ko',
                            'text': encoded
                        },
                        headers={
                            'X-NCP-APIGW-API-KEY-ID': config['papago']['key'],
                            'X-NCP-APIGW-API-KEY': config['papago']['secret']
                        })

                    if res.status_code != 200:
                        error_count += 1
                        raise Exception(res)

                    result = json.loads(res.content)['message']['result']['translatedText']
                    #print("r", result)
                    decoded = translator.decode_nouns(result)

                    papago[k] = decoded
                    #print("d", decoded)
                    print("")
                    translate_count += 1

                entity.papago = papago
                entity.save()

        print("succ", translate_count, "err", error_count)
