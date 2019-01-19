"""
통계 관련 데이터 뽑아내기용 템플릿 테그들
"""
import json

from django import template
from django.db.models import Count, Q, Sum
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from sunless_web.models import Noun, Discussion, EntityCate  # , EntityCate

register = template.Library()


@register.simple_tag
def get_progress():
    """ 카테고리별 번역 진행도 통계"""

    # order : "Nouns", "Events", "Qualities", "Exchanges", "Areas", "Personas
    nouns_total = Noun.objects.count() or 1
    nouns_trans = Noun.objects.exclude(Q(translate='') | Q(translate__isnull=True)).count()
    nouns_final = Noun.objects.exclude(Q(final='') | Q(final__isnull=True)).count()

    percentage_transed = [round(nouns_trans * 100 / nouns_total, 1),]
    percentage_partial = [round((nouns_final-nouns_trans) * 100 / nouns_total, 1),]

    for cate in EntityCate.objects.all():
        total = cate.entries.count() or 1
        partial = cate.entries.filter(status='partial').count()
        transed = cate.entries.filter(status='finished').count()

        percentage_partial.append(round(partial * 100 / total, 1))
        percentage_transed.append(round(transed * 100 / total, 1))

    return percentage_partial, percentage_transed


@register.simple_tag
def get_ranking():
    """번역 순위 가져오기"""

    ranker = get_user_model().objects.all().annotate(works=Count('translations')).order_by('-works')[:10]
    keys, values = zip(*[("%s위 %s" % (rank + 1, u.username), u.works) for rank, u in enumerate(ranker)])

    return {
        "k": mark_safe(json.dumps(keys)),
        "v": json.dumps(values)
    }


@register.simple_tag
def get_recent():
    """최근 댓글 가져오기"""

    recent = Discussion.objects.order_by('-created_at')[:5]

    return [{
        'user': (discuss.user.username if discuss.user else 'System'),
        'entry': discuss.translate.entry.pk,
        'link': discuss.translate.entry.get_absolute_url,
        'summary': discuss.msg[:20]
    } for discuss in recent]
