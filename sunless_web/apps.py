from suit.apps import DjangoSuitConfig
from suit.menu import ParentItem, ChildItem


class SunlessConfig(DjangoSuitConfig):
    menu = (
        ParentItem('명사 사전', children=[
            ChildItem(model='sunless_web.nouncate'),
            ChildItem(model='sunless_web.noun'),
            ChildItem(model='sunless_web.entitycate'),
        ], icon='fa fa-leaf'),
        ParentItem('번역 작업 V2', children=[
            ChildItem(model='sunless_web.entrypath'),
            ChildItem(model='sunless_web.entry'),
        ], icon='fa fa-telegram'),
        ParentItem('사용자 관리', children=[
            ChildItem(model='auth.user'),
            ChildItem(model='auth.group'),
        ], icon='fa fa-users'),
        ParentItem('씨봇이 관리', children=[
            ChildItem(model='sunless_web.conversation'),
            ChildItem(model='sunless_web.patch'),
        ], icon='fa fa-telegram'),
    )

    verbose_name = '라라라'
