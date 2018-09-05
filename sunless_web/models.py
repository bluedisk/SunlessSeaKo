import hashlib
import random

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db.models.functions import Length
from django.urls import reverse
from django.utils.safestring import mark_safe

from django.core.cache import cache
from modules.papago import papago

import re


class EntityCate(models.Model):
    class Meta:
        verbose_name = '번역 파일'
        verbose_name_plural = '번역 파일 목록'

    name = models.CharField(max_length=60, primary_key=True)

    def __str__(self):
        return self.name


class Entity(models.Model):
    class Meta:
        verbose_name = '번역 대상'
        verbose_name_plural = '번역 대상 목록'

    def __str__(self):
        return self.path()

    @staticmethod
    def make_hash(cate, parent, key):
        text = "%s-%s-%s" % (cate, parent, key)
        return hashlib.md5(text.encode('utf8')).hexdigest()

    def path(self):
        return "%s / %s / %s" % (self.cate.name, self.parent, self.key)
    path.short_description = '위치'

    def summary(self):
        return "%s..." % (self.original.get('Name', '') or '' +
                          self.original.get('Teaser', '') or '' +
                          self.original.get('Description', '') or '')[:50]
    summary.short_description = '요약'

    def checker_list(self):
        return mark_safe(", ".join(["<a href='work/auth/user/%s/change'>%s</a>" % (c.pk, c.username) for c in self.checker.all()]))
    checker_list.read_only = True
    checker_list.short_description = '검수자 목록'

    def checker_count(self):
        return self.checker.count()
    checker_count.short_description = '검수자 수'

    cate = models.ForeignKey('EntityCate',
                             verbose_name='소속 파일',
                             related_name='entities',
                             db_index=True,
                             on_delete=models.CASCADE
                             )

    key = models.IntegerField('파일상 ID', db_index=True)
    hash = models.CharField('HashHex V1', max_length=70, db_index=True, unique=True)
    hash_v2 = models.CharField('HashHex v2', max_length=70, db_index=True, unique=True, null=True, blank=True)

    parent = models.CharField('부모 항목', max_length=70, null=True, blank=True)

    original = JSONField('Original Text(JSON)', default={})
    marked = JSONField('Noun marked Original Text(JSON)', default={})
    reference = JSONField('Reference Text(JSON)', default={})
    google = JSONField('Google Translated Text(JSON)', default={})
    papago = JSONField('Papago Translated Text(JSON)', default={})
    translate = JSONField('Translated Text(JSON)', default={})
    final = JSONField('Final Text(JSON)', default={})

    checker = models.ManyToManyField(get_user_model(), related_name="entities")

    translated = models.IntegerField('초벌 번역 숫자', default=0)
    finalized = models.IntegerField('변역 확정 숫자', default=0)
    items = models.IntegerField('변역 항목 숫자', default=0)

    TRANSLATE_STATUS = (
        ('none', '안됨'),
        ('in', '진행 중'),
        ('done', '완료')
    )
    status = models.CharField('번역 상태', max_length=4, choices=TRANSLATE_STATUS, default='none')
    error = models.TextField('error', null=True)

    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    STATUS_HTML = {
        'none': '<span style="color:#a08080;"><i class="far fa-times-circle"></i> 안됨</span>',
        'in': '<span style="color:#8080a0;"><i class="far fa-edit"></i> 진행</span>',
        'done': '<span style="color:#80a080;"><i class="far fa-check-circle"></i> 완료</span>'
    }

    def status_html(self):
        return mark_safe(self.STATUS_HTML.get(self.status, 'Error!'))
    status_html.short_description = '번역상태'

    def check_translated(self):
        items = 0
        transed = 0
        finaled = 0

        for field in ('Name', 'Teaser', "Description"):
            if self.original.get(field, None):
                items += 1
                if self.final.get(field, None):
                    transed += 1
                if self.translate.get(field, None):
                    finaled += 1

        return items, transed, finaled

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.items, self.translated, self.finalized = self.check_translated()
        if not self.translated and not self.finalized:
            self.status = 'none'
        elif self.finalized == self.items:
            self.status = 'done'
        else:
            self.status = 'in'

        super(Entity, self).save(force_insert, force_update, using, update_fields)


class Entry(models.Model):
    class Meta:
        verbose_name = '번역 대상'
        verbose_name_plural = '번역 대상 목록'

    def __str__(self):
        return self.path

    path = models.CharField('위치', max_length=256, default='')

    def summary(self):
        return "%s..." % self.text[:50]

    summary.short_description = '요약'

    cate = models.ForeignKey('EntityCate',
                             verbose_name='소속 파일',
                             related_name='entries',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE
                             )

    hash_v1 = models.CharField('HashHex v1', max_length=70, db_index=True, null=True, blank=True)
    hash_v2 = models.CharField('HashHex v2', max_length=70, db_index=True, unique=True)

    text_en = models.TextField('원문', null=True, blank=True)
    text_kr = models.TextField('영한번역', null=True, blank=True)
    text_jp = models.TextField('일어', null=True, blank=True)
    text_jpkr = models.TextField('일한번역', null=True, blank=True)

    checker = models.ManyToManyField(get_user_model(), related_name="entries")

    TRANSLATE_STATUS = (
        ('none', '안됨'),
        ('proto', '검수 필요'),
        ('discuss', '논의 필요'),
        ('verified', '완료')
    )
    status = models.CharField('번역 상태', max_length=10, choices=TRANSLATE_STATUS, default='none')

    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    STATUS_HTML = {
        'none': '<span style="color:#a08080;"><i class="far fa-times-circle"></i> 안됨</span>',
        'proto': '<span style="color:#8080a0;"><i class="far fa-edit"></i> 검수 필요</span>',
        'discuss': '<span style="color:#8080a0;"><i class="far fa-edit"></i> 논의 필요</span>',
        'verified': '<span style="color:#80a080;"><i class="far fa-check-circle"></i> 완료</span>'
    }

    def status_html(self):
        return mark_safe(self.STATUS_HTML.get(self.status, 'Error!'))
    status_html.short_description = '번역상태'


class Discuss(models.Model):
    class Meta:
        verbose_name = '논의'
        verbose_name_plural = '논의 목록'

    def __str__(self):
        return f"{self.user.get_full_name()} : {self.entry.hash_v2}"

    user = models.ForeignKey(get_user_model(), related_name='discusses', on_delete=models.CASCADE)
    entry = models.ForeignKey('Entry', related_name='discusses', on_delete=models.CASCADE)
    likes = models.ManyToManyField(get_user_model(), verbose_name='좋아요')
    text = models.TextField('내용')


class NounCate(models.Model):
    class Meta:
        verbose_name = '명사 분류'
        verbose_name_plural = '명사 분류 목록'

    def __str__(self):
        return mark_safe(f"<i class='{self.icon}'></i> {self.name}")

    name = models.CharField('명사 분류', max_length=50)
    icon = models.CharField('아이콘 클래스', max_length=50, default='fas fa-book')


def make_function_with_group(nouns, f):
    def nid_function(g):
        nid = int(g.groups()[0])
        return f(nid, nouns[nid] if nouns else None)

    return nid_function


class Noun(models.Model):
    class Meta:
        verbose_name = '명사'
        verbose_name_plural = '명사 사전'

    mention_ex = re.compile(r'@\[.+?\]\((\d{4})\)')
    noun_ex = re.compile(r'\!N(\d{4})\!')

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse('admin:{}_{}_change'.format(self._meta.app_label, self._meta.model_name), args=(self.pk,))

    @staticmethod
    def nid_to_mention(text):
        nouns = cache.get("noun_dict") or Noun.make_dict()
        text = Noun.noun_ex.sub(
            make_function_with_group(nouns, lambda nid, words: "@[%s](%04d)" % (words[2], nid)),
            text)
        return text

    @staticmethod
    def mention_to_nid(text):
        text = Noun.mention_ex.sub(make_function_with_group(None, lambda nid, _: "!N%04d!" % nid), text)
        return text

    @staticmethod
    def nid_to_en(text):
        nouns = cache.get("noun_dict") or Noun.make_dict()
        text = Noun.noun_ex.sub(make_function_with_group(nouns, lambda nid, words: words[0]), text)
        return text

    @staticmethod
    def nid_to_ko(text):
        nouns = cache.get("noun_dict") or Noun.make_dict()
        text = Noun.noun_ex.sub(make_function_with_group(nouns, lambda nid, words: words[1]), text)
        return text

    @staticmethod
    def make_dict():
        print("Making dict!")
        nouns = {}
        for noun in Noun.objects.all().order_by(Length('name').desc()):
            key = noun.pk

            # order: en, ko, mixed
            if noun.final:
                nouns[key] = (noun.name, noun.final, "%s(%s)" % (noun.name, noun.final))
            elif noun.translate:
                nouns[key] = (noun.name, noun.translate, "%s(%s)" % (noun.name, noun.translate))
            elif noun.papago:
                nouns[key] = (noun.name, noun.papago, "%s(%s)" % (noun.name, noun.papago))
            elif noun.google:
                nouns[key] = (noun.name, noun.google, "%s(%s)" % (noun.name, noun.google))
            else:
                nouns[key] = (noun.name, noun.name, noun.name)

        cache.set('noun_dict', nouns, 60*5)
        return nouns

    cate = models.ForeignKey(NounCate, on_delete=models.CASCADE)
    name = models.CharField('이름', max_length=100, unique=True)
    reference = models.TextField('참고의견', null=True, blank=True, default='')
    google = models.CharField('구글', max_length=100, null=True, blank=True, default='')
    papago = models.CharField('파파고', max_length=100, null=True, blank=True, default='')
    translate = models.CharField('번역', max_length=100, null=True, blank=True, default='')
    final = models.CharField('최종본', max_length=100, null=True, blank=True, default='')

    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.papago:
            self.papago = papago(self.name)
        super(Noun, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
        cache.clear()
        Noun.make_dict()


class Conversation(models.Model):
    class Meta:
        verbose_name = "대화"
        verbose_name_plural = "대화집"

    def __str__(self):
        return self.pattern

    def __init__(self, *args, **kwargs):
        super(Conversation, self).__init__(*args, **kwargs)
        self.compiled = re.compile(self.pattern)

    def findall(self, text):
        if not self.compiled:
            return []

        return self.compiled.findall(text)

    def pick_one(self):
        return random.choice(self.answers.all())

    compiled = re.compile('^')
    pattern = models.CharField('패턴', max_length=100)
    chance = models.FloatField('응답확률', default=0.0)


class Answer(models.Model):
    class Meta:
        verbose_name = "응답"
        verbose_name_plural = "응답들"

    def __str__(self):
        return self.answer

    answer = models.CharField('응답', max_length=300)
    parent = models.ForeignKey('Conversation',
                               verbose_name='대화',
                               related_name="answers",
                               on_delete=models.CASCADE)


class Patch(models.Model):
    class Meta:
        verbose_name = "패치"
        verbose_name_plural = "패치 목록"

    def __str__(self):
        return str(self.created_at)

    def get_absolute_url(self):
        return self.file.url

    def get_trans_percent(self):
        return f'{self.translated * 100 / self.items:.2f}'

    def get_final_percent(self):
        return f'{self.finalized * 100 / self.items:.2f}'

    file = models.FileField('패치파일')

    translated = models.IntegerField('변역 완료 숫자', default=0)
    finalized = models.IntegerField('변역 확정 숫자', default=0)
    items = models.IntegerField('변역 항목 숫자', default=0)

    download = models.IntegerField('다운로드 수', default=0)

    created_at = models.DateTimeField('생성일', auto_now_add=True)


class TelegramUser(models.Model):
    class Meta:
        verbose_name = "텔레그램 유저"
        verbose_name_plural = "텔레그램 유저 목록"

    def __str__(self):
        return str(self.telegram_id)

    user = models.OneToOneField(get_user_model(), primary_key=True, related_name='telegram', on_delete=models.deletion.CASCADE)
    telegram_id = models.IntegerField("Telegram ID")


# proxy

class AreaEntity(Entity):
    class Meta:
        verbose_name = "지역"
        verbose_name_plural = "지역 목록"
        proxy = True


class OtherEntity(Entity):
    class Meta:
        verbose_name = "번역 대상"
        verbose_name_plural = "번역 대상 목록"
        proxy = True
