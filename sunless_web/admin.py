from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres.fields import JSONField
from django import forms
from django.db import models
from django.utils.translation import gettext as _


from .models import Entity, EntityCate, Noun, NounCate, Conversation, Answer
from mentions.widgets import ElasticTextarea, TranslateTextarea

TRANS_HELP = None

admin.site.site_header = 'Sunless Sea 한글화'
admin.site.index_title = '데이터 관리'
admin.site.site_title = 'Sunless Sea 한글화'
admin.site.index_template = 'admin/statistics.html'


class EntityForm(forms.ModelForm):
    class Meta:
        model = Entity
        exclude = ('create_at', 'update_at', 'cate', 'key', 'hash', 'parent')

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

    EDITOR_OPTIONS = {
        "toolbar": [],
        "extraPlugins": 'autogrow'
    }

    Name_original = forms.CharField(label='원문', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
    Name_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
    Name_papago = forms.CharField(label='파파고', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
    Name_google = forms.CharField(label='구글', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
    Name_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
    Name_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))

    Teaser_original = forms.CharField(label='원문', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Teaser_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Teaser_papago = forms.CharField(label='파파고', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Teaser_google = forms.CharField(label='구글', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Teaser_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Teaser_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))

    Description_original = forms.CharField(label='원문', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Description_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Description_papago = forms.CharField(label='파파고', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Description_google = forms.CharField(label='구글', disabled=True, help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Description_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
    Description_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))

    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)

        if self.instance:
            for trans_type in self.TRANS_TYPES:
                trans = getattr(self.instance, trans_type)
                if not trans:
                    continue

                for field in self.FIELDS:
                        value = trans.get(field, '')
                        self.initial[f'{field}_{trans_type}'] = mark_safe(value)

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
            'all': [
                'https://use.fontawesome.com/releases/v5.0.13/css/all.css',
                'css/base.css'
                    ]
        }

        js = [
        ]

    form = EntityForm

    readonly_fields = ('cate', 'key', 'parent', 'hash','checker_list')
    search_fields = ['key', 'hash', 'original', 'google', 'papago', 'translate', 'final']
    list_display_links = ['path', 'summary']
    list_filter = [CheckerFilter, 'translated', 'cate', 'parent']
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Info', {
                'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
                'fields': [('cate', 'key', 'parent', 'hash')],
            })]

        if not obj or obj.original['Name']:
            autolist = []
            if not obj or obj.papago.get('Name', None):
                autolist.append('Name_papago')

            if not obj or obj.google.get('Name', None):
                autolist.append('Name_google')

            row = ('Name', {
                'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
                'fields': ['Name_original',
                           autolist,
                           ('Name_translate', 'Name_final'),
                           'Name_reference']
            })

            fieldsets.append(row)

        if not obj or obj.original['Teaser']:
            autolist = []
            if not obj or obj.papago.get('Teaser', None):
                autolist.append('Teaser_papago')

            if not obj or obj.google.get('Teaser', None):
                autolist.append('Teaser_google')

            fieldsets.append(('Teaser', {
                'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
                'fields': ['Teaser_original'] + autolist +
                          ['Teaser_translate', 'Teaser_final', 'Teaser_reference']
            }))

        if not obj or obj.original['Description']:
            autolist = []
            if not obj or obj.papago.get('Description', None):
                autolist.append('Description_papago')

            if not obj or obj.google.get('Description', None):
                autolist.append('Description_google')

            fieldsets.append(('Description', {
                'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
                'fields': ['Description_original'] + autolist +
                          ['Description_translate', 'Description_final', 'Description_reference']
            }))

        if request.user.is_superuser:
            fieldsets.append(('Debug', {'fields': ['original', 'checker_list']}))

        return fieldsets

    def get_list_display(self, request):
        def am_i_checked_it(obj):
            return mark_safe(
                '<span style="color:#80a080;"><i class="far fa-check-circle"></i> 응</span>'
                if obj.checker.filter(pk=request.user.pk).exists()
                else '<span style="color:#a08080;"><i class="far fa-times-circle"></i> 아니</span>'
            )

        am_i_checked_it.allow_tags = True
        am_i_checked_it.short_description = '내가 체크했나?'

        if request.user.is_superuser:
            return ['path', 'summary', am_i_checked_it, 'checker_count', 'update_at']
        else:
            return ['path', 'summary', am_i_checked_it, 'update_at']

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


@admin.register(EntityCate)
class EntityCateAdmin(admin.ModelAdmin):
    pass


@admin.register(NounCate)
class NounCateAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ['https://use.fontawesome.com/releases/v5.0.13/css/all.css']
        }


class NounForm(forms.ModelForm):
    class Meta:
        model = Noun
        widgets = {'reference': ElasticTextarea()}
        exclude = ['_']


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
        models.TextField: {'widget': ElasticTextarea()},
    }

    def cate_safe(self, obj):
        return mark_safe(obj.cate)


class AnswerInline(admin.TabularInline):
    model = Answer


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    inlines = (AnswerInline, )
