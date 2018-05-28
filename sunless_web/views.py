from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from .models import Noun, Patch


@cache_page(60 * 5)
def nouns(requests):
    result = []

    for noun in Noun.objects.all():
        result.append({
            'uid': '%s:%s' % (noun.cate.name, noun.id),
            'value': noun.name,
        })

    return JsonResponse(result, safe=False)


def home(request):
    return render(request, "home.html", {"patch": Patch.objects.order_by('-created_at').first()})


def download(request, patch_id):
    patch = Patch.objects.get(pk=patch_id)
    patch.download += 1
    patch.save()

    return HttpResponseRedirect(patch.file.url)
