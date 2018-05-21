from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils.safestring import mark_safe


class EntityFile(models.Model):
    class Meta:
        verbose_name = '대상 파일'
        verbose_name_plural = '대상 파일 목록'

    filename = models.CharField(max_length=60)

    def __str__(self):
        return self.filename


class Entity(models.Model):
    class Meta:
        verbose_name = '번역 대상'
        verbose_name_plural = '번역 대상 목록'

    def __str__(self):
        return self.hash

    file = models.ForeignKey('EntityFile',
                             verbose_name='소속 파일',
                             related_name='entities',
                             db_index=True,
                             on_delete=models.CASCADE
                             )

    key = models.IntegerField('파일상 ID', db_index=True)
    hash = models.CharField('HashHex', max_length=70, db_index=True, unique=True)

    parent = models.CharField('부모 항목', max_length=70, null=True, blank=True)

    original = JSONField('Original Text(JSON)', default={})
    reference = JSONField('Reference Text(JSON)', default={})
    google = JSONField('Google Translated Text(JSON)', default={})
    papago = JSONField('Papago Translated Text(JSON)', default={})
    translate = JSONField('Translated Text(JSON)', default={})
    final = JSONField('Final Text(JSON)', default={})

    checker = models.ManyToManyField(get_user_model(), related_name="entities")
    noun_error = models.BooleanField('has error', default=False)

    create_at = models.DateTimeField('생성일', auto_now_add=True)
    update_at = models.DateTimeField('수정일', auto_now=True)


class NounCate(models.Model):
    class Meta:
        verbose_name = '명사 분류'
        verbose_name_plural = '명사 분류 목록'

    def __str__(self):
        return mark_safe(f"<i class='{self.icon}'></i> {self.name}")

    name = models.CharField('명사 분류', max_length=50)
    icon = models.CharField('아이콘 클래스', max_length=50, default='fas fa-book')


class Noun(models.Model):
    class Meta:
        verbose_name = '명사'
        verbose_name_plural = '명사 사전'

    def __str__(self):
        return self.name

    cate = models.ForeignKey(NounCate, on_delete=models.CASCADE)
    name = models.CharField('이름', max_length=100)
    reference = models.TextField('참고의견', null=True, blank=True, default='')
    google = models.CharField('구글', max_length=100, null=True, blank=True, default='')
    papago = models.CharField('파파고', max_length=100, null=True, blank=True, default='')
    translate = models.CharField('번역', max_length=100, null=True, blank=True, default='')
    final = models.CharField('최종본', max_length=100, null=True, blank=True, default='')

