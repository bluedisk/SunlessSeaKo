from modules.config import config

import json
import requests
from pprint import pprint

PAPAGO_ENDPOINT = 'https://naveropenapi.apigw.ntruss.com/nmt/v1/translation'


def papago(text, exception_on_error=False):
    res = requests.post(PAPAGO_ENDPOINT, data={
            'source': 'en',
            'target': 'ko',
            'text': text
        },
        headers={
            'X-NCP-APIGW-API-KEY-ID': config['papago']['key'],
            'X-NCP-APIGW-API-KEY': config['papago']['secret']
        })

    if res.status_code != 200:
        print("[PAPAGO] error on ", text)
        pprint(res)
        if exception_on_error:
            raise Exception(res)
        return None

    return json.loads(res.content)['message']['result']['translatedText']


