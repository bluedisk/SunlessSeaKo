from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres.fields import JSONField
from django import forms
from django.db import models
from django.utils.translation import gettext as _

from urllib.parse import parse_qsl

from .models import EntityCate, Noun, NounCate, Conversation, Answer, Patch, TelegramUser, Entry, Translation, EntryPath, Discussion
from mentions.widgets import ElasticTextarea, TranslateTextarea

TRANS_HELP = None

admin.site.site_header = 'Sunless Sea 한글화'
admin.site.index_title = '데이터 관리'
admin.site.site_title = 'Sunless Sea 한글화'
admin.site.index_template = 'admin/statistics.html'


# class EntityForm(forms.ModelForm):
#     class Meta:
#         model = Entity
#         exclude = ('created_at', 'updated_at', 'cate', 'key', 'hash', 'parent')
#
#     TRANS_TYPES = (
#         'marked',
#         'reference',
#         'papago',
#         'translate',
#         'final',
#     )
#
#     FIELDS = (
#         'Name',
#         'Teaser',
#         'Description'
#     )
#
#     Name_marked = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
#     Name_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
#     Name_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
#     Name_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
#     Name_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 30, 'rows': 1}))
#
#     Teaser_marked = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
#     Teaser_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
#     Teaser_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
#     Teaser_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
#     Teaser_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 100, 'rows': 1}))
#
#     Description_marked = forms.CharField(label='원문', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 150, 'rows': 1}))
#     Description_reference = forms.CharField(label='의견', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 150, 'rows': 1}))
#     Description_papago = forms.CharField(label='파파고', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 150, 'rows': 1}))
#     Description_translate = forms.CharField(label='번역', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 150, 'rows': 1}))
#     Description_final = forms.CharField(label='최종본', help_text=TRANS_HELP, required=False, widget=TranslateTextarea({'cols': 150, 'rows': 1}))
#
#     def __init__(self, *args, **kwargs):
#         super(EntityForm, self).__init__(*args, **kwargs)
#
#         if self.instance:
#             for trans_type in self.TRANS_TYPES:
#                 trans = getattr(self.instance, trans_type)
#
#                 if not trans:
#                     continue
#
#                 for field in self.FIELDS:
#                     if field in trans:
#                         value = Noun.nid_to_mention(trans[field])
#                         self.initial[f'{field}_{trans_type}'] = mark_safe(value)
#
#     def save(self, commit=True):
#         return super(EntityForm, self).save(commit)


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


class MyRequest:
    def __init__(self, **entries):
        self.__dict__.update(entries)


# @admin.register(Entity)
# class EntityAdmin(admin.ModelAdmin):
#
#     class Media:
#         css = {
#             'all': [
#                 'https://use.fontawesome.com/releases/v5.0.13/css/all.css',
#                 'css/base.css'
#                     ]
#         }
#
#         js = [
#         ]
#
#     form = EntityForm
#
#     search_fields = ['key', 'hash', 'original', 'papago', 'translate', 'final'] # 'google',
#     list_display_links = ['path', 'summary']
#     list_filter = [CheckerFilter, 'status', 'cate', 'parent']
#     formfield_overrides = {
#         JSONField: {'widget': JSONEditorWidget},
#     }
#
#     def get_fieldsets(self, request, obj=None):
#         fieldsets = [
#             ('Info', {
#                 'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
#                 'fields': [('cate', 'key', 'parent', 'hash')],
#             })]
#
#         if not obj or obj.original['Name']:
#             autolist = []
#             if not obj or obj.papago.get('Name', None):
#                 autolist.append('Name_papago')
#
#             # if not obj or obj.google.get('Name', None):
#             #     autolist.append('Name_google')
#
#             row = ('Name', {
#                 'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
#                 'fields': ['Name_marked',
#                            autolist,
#                            ('Name_translate', 'Name_final'),
#                            'Name_reference']
#             })
#
#             fieldsets.append(row)
#
#         if not obj or obj.original['Teaser']:
#             autolist = []
#             if not obj or obj.papago.get('Teaser', None):
#                 autolist.append('Teaser_papago')
#
#             # if not obj or obj.google.get('Teaser', None):
#             #     autolist.append('Teaser_google')
#
#             fieldsets.append(('Teaser', {
#                 'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
#                 'fields': ['Teaser_marked'] + autolist +
#                           ['Teaser_translate', 'Teaser_final', 'Teaser_reference']
#             }))
#
#         if not obj or obj.original['Description']:
#             autolist = []
#             if not obj or obj.papago.get('Description', None):
#                 autolist.append('Description_papago')
#
#             # if not obj or obj.google.get('Description', None):
#             #     autolist.append('Description_google')
#
#             fieldsets.append(('Description', {
#                 'description': '고유명사를 추가하시려면 @를 누르고 타이핑해주세요',
#                 'fields': ['Description_marked'] + autolist +
#                           ['Description_translate', 'Description_final', 'Description_reference']
#             }))
#
#         if request.user.is_superuser:
#             fieldsets.append(('Debug', {'fields': ['original', 'checker_list']}))
#
#         return fieldsets
#
#     def get_readonly_fields(self, request, obj=None):
#         readonly = ['cate', 'key', 'parent', 'hash', 'checker_list']
#         #
#         # if not obj:
#         #     return readonly
#         #
#         # for field in EntityForm.FIELDS:
#         #     if obj.original[field]:
#         #         readonly.append(f'{field}_marked')
#         #         if obj.papago.get(field, None):
#         #             readonly.append(f'{field}_papago')
#         #
#         #         if obj.google.get(field, None):
#         #             readonly.append(f'{field}_google')
#
#         return readonly
#
#     def get_list_display(self, request):
#         def am_i_checked_it(obj):
#             return mark_safe(
#                 '<span style="color:#80a080;"><i class="far fa-check-circle"></i> 응</span>'
#                 if obj.checker.filter(pk=request.user.pk).exists()
#                 else '<span style="color:#a08080;"><i class="far fa-times-circle"></i> 아니</span>'
#             )
#
#         am_i_checked_it.allow_tags = True
#         am_i_checked_it.short_description = '내가 체크했나?'
#
#         if request.user.is_superuser:
#             return ['path', 'summary', am_i_checked_it, 'status_html', 'checker_count', 'updated_at']
#         else:
#             return ['path', 'summary', am_i_checked_it, 'status_html', 'updated_at']
#
#     def save_model(self, request, obj, form, change):
#         obj.checker.add(request.user)
#
#         for trans_type in ['papago', 'marked', 'reference', 'translate', 'final']: #'google',
#             trans = {}
#
#             for field in form.FIELDS:
#                 data = form.cleaned_data[f'{field}_{trans_type}']
#
#                 if data:
#                     trans[field] = Noun.mention_to_nid(data)
#                 else:
#                     trans[field] = ''
#
#             setattr(obj, trans_type, trans)
#
#         super(EntityAdmin, self).save_model(request, obj, form, change)
#
#     def response_change(self, request, obj):
#         """
#         Determines the HttpResponse for the change_view stage.
#         """
#         if "_viewnext" in request.POST:
#             opts = self.model._meta
#             msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
#                    {'name': force_text(opts.verbose_name),
#                     'obj': force_text(obj)})
#
#             preserved_filter = request.GET.get('_changelist_filters')
#             filters = dict(parse_qsl(preserved_filter))
#             setattr(request, "GET", filters)
#             next_obj = self.get_changelist_instance(request)
#             next_obj = next_obj.get_queryset(request)
#             next_obj = next_obj.filter(id__lt=obj.id).first()
#
# #            next_obj = next_obj.order_by('id')[:1]
#             if next_obj:
#                 self.message_user(request, msg)
#                 setattr(request, "GET", {'_changelist_filters': preserved_filter})
#                 return HttpResponseRedirect(
#                     reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
#                             args=(next_obj.pk,)) + "?" + self.get_preserved_filters(request),
#                 )
#         elif "_viewprev" in request.POST:
#             opts = self.model._meta
#             msg = (_('The %(name)s "%(obj)s" was changed successfully.') %
#                    {'name': force_text(opts.verbose_name),
#                     'obj': force_text(obj)})
#
#             preserved_filter = request.GET.get('_changelist_filters')
#             filters = dict(parse_qsl(preserved_filter))
#             setattr(request, "GET", filters)
#             next_obj = self.get_changelist_instance(request).get_queryset(request)
#             next_obj = next_obj.filter(id__gt=obj.id).first()
#
# #            next_obj = next_obj.order_by('id')[:1]
#             if next_obj:
#                 self.message_user(request, msg)
#                 setattr(request, "GET", {'_changelist_filters': preserved_filter})
#                 return HttpResponseRedirect(
#                     reverse('admin:{}_{}_change'.format(obj._meta.app_label, obj._meta.model_name),
#                             args=(next_obj.pk,)) + "?" + self.get_preserved_filters(request),
#                 )
#
#         return super(EntityAdmin, self).response_change(request, obj)


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

    list_display = ['cate_safe', 'name', 'reference', 'papago', 'translate', 'final'] # 'google',
    list_display_links = ['name']
    list_editable = ['reference',  'papago', 'translate', 'final'] # 'google',
    list_filter = ('cate',)

    search_fields = ['name', 'papago', 'translate', 'final']

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


@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'file', 'download']


class ProfileInline(admin.StackedInline):
    model = TelegramUser
    can_delete = False
    verbose_name_plural = 'Telegram'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class EntryInline(admin.StackedInline):
    model = Entry
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': ElasticTextarea()},
    }

    readonly_fields = ['text_en', 'text_jp', 'text_jpkr', 'status', 'basepath', 'object']

    fieldsets = [
            ('Location', {
                'description': '게임상의 데이터 위치 정보',
                'fields': (('object', 'status'), ),
            }),
            ('Translation', {
                'description': '번역 진행',
                'fields': ('text_en', 'text_jp', 'text_jpkr', ),
            }),
    ]


@admin.register(EntryPath)
class EntryPathAdmin(admin.ModelAdmin):
    inlines = (EntryInline, )
    readonly_fields = ('name', )
    search_fields = ("name", "entries__text_en", "entries__text_jpkr", "entries__translations__text")

    list_display = ('name', 'status', 'entry_count')
    list_filter = ('status', 'cate')

    change_form_template = "admin/translate.html"


class DiscussionInline(admin.TabularInline):
    model = Discussion

    readonly_fields = ['translate']

    formfield_overrides = {
        models.TextField: {'widget': ElasticTextarea()},
    }


class TranslationInline(admin.TabularInline):
    model = Translation
    inlines = (DiscussionInline, )

    formfield_overrides = {
        models.TextField: {'widget': ElasticTextarea()},
    }


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = (TranslationInline, )

    list_display = ('hash_v2', 'fullpath', 'summary')
    list_filter = ('status', 'path__cate')

    search_fields = ['basepath', 'object', 'hash_v1', 'hash_v2', 'text_en']
    readonly_fields = ['hash_v1', 'hash_v2', 'checker', 'text_en',
                       'text_jp', 'text_jpkr', 'status', 'basepath', 'object']

    fieldsets = [
            ('Location', {
                'description': '게임상의 데이터 위치 정보',
                'fields': ['hash_v1', 'hash_v2', ('basepath', 'object')],
            }),
            ('Status', {
                'description': '진행상태',
                'fields': ['status', 'checker'],
            }),
            ('Translation', {
                'description': '번역 진행',
                'fields': [('text_en', ), ('text_jpkr', 'text_jp')],
            }),
    ]

    formfield_overrides = {
        models.TextField: {'widget': ElasticTextarea()},
    }


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
