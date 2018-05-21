from django.core.management.base import BaseCommand

from modules.config import config

from sunless_web.models import Noun

import json
import requests
from pprint import pprint
from tqdm import tqdm

PAPAGO_ENDPOINT = 'https://naveropenapi.apigw.ntruss.com/nmt/v1/translation'


class Command(BaseCommand):

    def handle(self, *args, **options):
        translate_count = 0
        error_count = 0
        for noun in tqdm(Noun.objects.all()):
            if not noun.papago:
                res = requests.post(PAPAGO_ENDPOINT, data={
                        'source': 'en',
                        'target': 'ko',
                        'text': noun.name
                    },
                    headers={
                        'X-NCP-APIGW-API-KEY-ID': config['papago']['key'],
                        'X-NCP-APIGW-API-KEY': config['papago']['secret']
                    })

                if res.status_code != 200:
                    error_count += 1
                    print("error on ", noun.name)
                    pprint(res)
                    raise Exception(res)

                translate_count += 1
                noun.papago = json.loads(res.content)['message']['result']['translatedText']
                noun.save()

        print("succ", translate_count, "err", error_count)
