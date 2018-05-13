import os

_configs = {
    "prod": {
        "key": "",
        "sheetId": "",
        "force": False,
        "logMode": "telegram",
        "botToken": "",
        "botGroupId": 0
    },
    "dev": {
        "key": "",
        "sheetId": "",
        "force": True,
        "logMode": "print",
        "botToken": "",
        "botGroupId": 0
    },
}

config = _configs[os.environ.get('RUN_MODE', 'dev')]
