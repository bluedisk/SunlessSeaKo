import json

from django import template
from django.db.models import Count, Q, Sum
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from sunless_web.models import Entity, Noun #, EntityCate

register = template.Library()


@register.simple_tag
def get_progress():
    # order : "Nouns", "Events", "Qualities", "Exchanges", "Areas", "Personas
    nouns_trans = Noun.objects.exclude(Q(translate='') | Q(translate__isnull=True)).count()
    nouns_final = Noun.objects.exclude(Q(final='') | Q(final__isnull=True)).count()

    total = [Noun.objects.count()] + [0] * 5
    transed = [nouns_trans] + [0] * 5
    finaled = [nouns_final] + [0] * 5

    order = ("nouns", "events", "qualities", "exchanges", "areas", "personas")

    for count in Entity.objects.all().values('cate').annotate(cnt=Sum('items')):
        idx = order.index(count['cate'])
        total[idx] = count['cnt']

    for count in Entity.objects.all().values('cate').annotate(cnt=Sum('translated')):
        idx = order.index(count['cate'])
        transed[idx] = count['cnt']

    for count in Entity.objects.all().values('cate').annotate(cnt=Sum('finalized')):
        idx = order.index(count['cate'])
        finaled[idx] = count['cnt']

    percentage_trans = []
    percentage_final = []
    for idx, (total, final, transed)in enumerate(zip(total, finaled, transed)):
        total = total or 1

        percentage_trans.append(round((transed-final)*100/total, 1))
        percentage_final.append(round(final*100/total, 1))

    return percentage_trans, percentage_final


@register.simple_tag
def get_ranking():
    ranker = get_user_model().objects.all().annotate(works=Count('entities')).order_by('-works')[:10]
    keys, values = zip(*[("%s위 %s" % (rank+1, u.username), u.works) for rank, u in enumerate(ranker)])

    return {
        "k": mark_safe(json.dumps(keys)),
        "v": json.dumps(values)
    }
