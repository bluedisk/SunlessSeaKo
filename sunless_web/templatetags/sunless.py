from django import template
from django.db.models import Count, Q

from sunless_web.models import Entity, EntityCate, Noun

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

    for count in Entity.objects.all().values('cate').annotate(cnt=Count('cate')):
        idx = order.index(count['cate'])
        total[idx] = count['cnt']

    for count in Entity.objects.filter(translated=True).values('cate').annotate(cnt=Count('cate')):
        idx = order.index(count['cate'])
        transed[idx] = count['cnt']

    for count in Entity.objects.filter(final=True).values('cate').annotate(cnt=Count('cate')):
        idx = order.index(count['cate'])
        finaled[idx] = count['cnt']

    percentage_trans = []
    percentage_final = []
    for idx, (total, final, transed)in enumerate(zip(total, finaled, transed)):
        percentage_trans.append(round((transed-final)*100/total, 1))
        percentage_final.append(round(final*100/total, 1))

    return percentage_trans, percentage_final
