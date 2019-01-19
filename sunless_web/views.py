import json
from json import JSONDecodeError

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Noun, Patch, Discussion, Translation, Entry


def nouns(_):
    nouns_dict = Noun.make_dict()
    result = [{'uid': '%04d' % key, 'value': values[2]} for key, values in nouns_dict.items()]

    return JsonResponse(result, safe=False)


def home(request):
    return render(request, "home.html", {
        "min_patch": Patch.objects.filter(patch_type='minimum').order_by('-created_at').first(),
        "full_patch": Patch.objects.filter(patch_type='full').order_by('-created_at').first()
    })


def download(request, patch_id):
    patch = Patch.objects.get(pk=patch_id)
    patch.download += 1
    patch.save()

    return HttpResponseRedirect(patch.file.url)


def like(request, action, target_type, target_id):
    target_model = {
        "discuss": Discussion,
        "trans": Translation
    }.get(target_type, None)

    if not target_model:
        return HttpResponseBadRequest()

    target = get_object_or_404(target_model, pk=target_id)

    if action == "like":
        target.likes.add(request.user)
    elif action == "unlike":
        target.likes.remove(request.user)
    else:
        return HttpResponseBadRequest()

    return JsonResponse([liker.pk for liker in target.likes.all()], safe=False)


@csrf_exempt
@staff_member_required
def add_translate(request, entry_id):
    entry = get_object_or_404(Entry, pk=entry_id)

    try:
        data = json.loads(request.body)
    except JSONDecodeError:
        return HttpResponseBadRequest()

    if data['postType'] == 'translate':
        trans = Translation()
        trans.entry = entry
        trans.user = request.user
        trans.text = data['postData']
        trans.save()
    else:
        return HttpResponseBadRequest()

    return JsonResponse(entry.to_json(), safe=False)


@csrf_exempt
@staff_member_required
def add_discuss(request, translate_id):
    translate = get_object_or_404(Translation, pk=translate_id)

    try:
        data = json.loads(request.body)
    except JSONDecodeError:
        return HttpResponseBadRequest()

    if data['postType'] == 'discuss':
        discuss = Discussion()
        discuss.translate = translate
        discuss.user = request.user
        discuss.msg = data['postData']
        discuss.save()

    else:
        return HttpResponseBadRequest()

    return JsonResponse(translate.to_json(), safe=False)
