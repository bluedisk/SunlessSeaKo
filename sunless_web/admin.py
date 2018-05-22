from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres.fields import JSONField
from django import forms
from django.forms.widgets import HiddenInput
from django.db import models
from django.utils.translation import gettext as _


from .models import Entity, EntityFile, Noun, NounCate
# from sunless_web.mentions.widgets import TranslateWidget
from mentions.widgets import ElasticTextarea

admin.site.site_header = 'Sunless Sea 한글화'
admin.site.index_title = '데이터 관리'
admin.site.site_title = 'Sunless Sea 한글화'

TRANS_HELP = None


class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        exclude = ('create_at', 'update_at', 'file', 'key', 'hash', 'parent')

    TRANS_TYPES = (
        'original',
        'reference',
        'papago',
        'google',
        'translate',
        'final',
    )

    FIELDS = (
        'Name',
        'Teaser',
        'Description'
    )

    Name_original = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '24', 'rows': '1'}))
    Name_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Name_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '24', 'rows': '1'}))
    Name_google = forms.CharField(label='구글', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '24', 'rows': '1'}))
    Name_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '24', 'rows': '1'}))
    Name_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '24', 'rows': '1'}))

    Teaser_original = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', 'rows': '1'}))
    Teaser_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Teaser_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', 'rows': '1'}))
    Teaser_google = forms.CharField(label='구글', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', 'rows': '1'}))
    Teaser_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', 'rows': '1'}))
    Teaser_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', 'rows': '1'}))

    Description_original = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Description_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Description_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Description_google = forms.CharField(label='구글', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Description_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))
    Description_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=ElasticTextarea({"cols": '100', "rows": '1'}))

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.FIELDS:
                origin = ''
                for trans_type in self.TRANS_TYPES:
                    value = getattr(self.instance, trans_type).get(field, '')
                    self.initial[f'{field}_{trans_type}'] = mark_safe(value)

                    if trans_type == 'original':
                        origin = value

                    if not value and (not origin or  (trans_type not in('translate', 'final'))):
                        self.fields[f'{field}_{trans_type}'].widget = forms.widgets.HiddenInput()

    def save(self, commit=True):
        return super(EntityForm, self).save(commit)


class CheckerFilter(SimpleListFilter):
    title = '내가 체크했는지 여부'
    parameter_name = 'amicheck'

    def lookups(self, request, model_admin):
        return (
            ("checked", '했음'),
            ("notyet", '안 했음'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'checked':
            return queryset.filter(id__in=request.user.entities.all())
        elif self.value() == 'notyet':
            return queryset.exclude(id__in=request.user.entities.all())


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):

    class Media:
        css = {
            'all': ['https://use.fontawesome.com/releases/v5.0.13/css/all.css']
        }
    form = EntityForm

    fieldsets = (
        ('Info', {
            'fields': [('file', 'key', 'parent', 'hash')],
        }),
        ('Name', {
            'fields': [('Name_original', 'Name_papago', 'Name_google'),
                       ('Name_translate', 'Name_final'),
                       'Name_reference']
        }),
        ('Teaser', {
            'fields': ['Teaser_original', 'Teaser_papago', 'Teaser_google',
                       'Teaser_translate', 'Teaser_final', 'Teaser_reference'
                       ]
        }),
        ('Description', {
            'fields': [('Description_original', 'Description_papago', 'Description_google'),
                       ('Description_translate', 'Description_final'),
                       'Description_reference']
        }),
        ('Debug', {
            'fields': ['original']
        })
    )

    readonly_fields = ('file', 'key', 'parent', 'hash')
    list_display_links = ['id']
    search_fields = ['key', 'original']
    list_filter = [CheckerFilter, 'file', 'parent']
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def get_list_display(self, request):
        def am_i_checked_it(obj):
            return mark_safe(
                '<span style="color:#80a080;"><i class="far fa-check-circle"></i> 응</span>'
                if obj.checker.filter(pk=request.user.pk).exists()
                else '<span style="color:#a08080;"><i class="far fa-times-circle"></i> 아니</span>'
            )

        am_i_checked_it.allow_tags = True
        am_i_checked_it.short_description = '내가 체크했나?'

        return ['file', 'id', am_i_checked_it, 'key', 'parent', 'update_at', 'create_at']

    def save_model(self, request, obj, form, change):
        obj.checker.add(request.user)

        for trans_type in form.TRANS_TYPES:
            trans = {}

            for field in form.FIELDS:
                if form.cleaned_data[f'{field}_{trans_type}']:
                    trans[field] = form.cleaned_data[f'{field}_{trans_type}']
                else:
                    trans[field] = ''

            setattr(obj, trans_type, trans)

        super(EntityAdmin, self).save_model(request, obj, form, change)

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        if "_viewnext" in request.POST:
            opts = self.model._meta
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_text(opts.verbose_name),
                    'obj': force_text(obj)})
            next_obj = obj.__class__.objects.filter(id__lt=obj.id).order_by('id')[:1]
            if next_obj:
                self.message_user(request, msg)
                return HttpResponseRedirect(
                    reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                            args=(next_obj[0].pk,)),
                )
        elif "_viewprev" in request.POST:
            opts = self.model._meta
            msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
                   {'name': force_text(opts.verbose_name),
                    'obj': force_text(obj)})
            next_obj = obj.__class__.objects.filter(id__gt=obj.id).order_by('id')[:1]
            if next_obj:
                self.message_user(request, msg)
                return HttpResponseRedirect(
                    reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
                            args=(next_obj[0].pk,)),
                )

        return super(EntityAdmin, self).response_change(request, obj)


@admin.register(EntityFile)
class EntityFileAdmin(admin.ModelAdmin):
    pass


@admin.register(NounCate)
class NounCateAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ['https://use.fontawesome.com/releases/v5.0.13/css/all.css']
        }


@admin.register(Noun)
class NounAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ['https://use.fontawesome.com/releases/v5.0.13/css/all.css']
        }

    list_display = ['cate_safe', 'name', 'reference', 'google', 'papago', 'translate', 'final']
    list_display_links = ['name']
    list_editable = ['reference', 'google', 'papago', 'translate', 'final']

    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size': 25})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 3, 'cols': 30})},
    }

    def cate_safe(self, obj):
        return mark_safe(obj.cate)
