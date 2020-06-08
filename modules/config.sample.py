import os

_configs = {
    "prod": {
        "key": "",
        "sheetId": "",
        "force": False,
        "logMode": "telegram",
        "botToken": "",
        "botGroupId": 0,
        "papago": {
            'key': '',
            'secret': '',
        },
        "database": {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '5432',
            }
        }
    },
    "dev": {
        "key": "",
        "sheetId": "",
        "force": True,
        "logMode": "print",
        "botToken": "",
        "botGroupId": 0,
        "papago": {
            'key': '',
            'secret': '',
        },
        "database": {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': '',
                'USER': '',
                'PASSWORD': '',
                'HOST': '',
                'PORT': '5432',
            }
        }
    },
}

config = _configs[os.environ.get('RUN_MODE', 'dev')]
