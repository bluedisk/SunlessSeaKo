from django.apps import AppConfig


class SunlessConfig(AppConfig):
    name = 'sunless_web'
    verbose_name = "번역 작업"


default_app_config = 'sunless_web.SunlessConfig'
