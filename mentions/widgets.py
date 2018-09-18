from django.forms.widgets import Textarea


class ElasticTextarea(Textarea):
    class Media:
        css = {
            'all': (
                'css/elastic.css',
            )
        }
        js = (
            'https://code.jquery.com/jquery-1.12.4.min.js',
            'js/elastic.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control js-elasticArea', 'style': '', 'rows': 1}
        if attrs:
            default_attrs.update(attrs)

        super(ElasticTextarea, self).__init__(default_attrs)


class TranslateTextarea(ElasticTextarea):
    class Media:
        css = {
            'all': (
                'https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css',
                'jquery-mentions/jquery.mentions.css',
            )
        }
        js = (
            'https://code.jquery.com/jquery-3.3.1.min.js',
            'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js',
            'jquery-mentions/jquery.mentions.js',
            'js/translate.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {'class': 'form-control js-elasticArea mentions', 'style': 'width: 100%'}
        if attrs:
            default_attrs.update(attrs)

        super(TranslateTextarea, self).__init__(default_attrs)

