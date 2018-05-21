from django.forms.widgets import Textarea


class TranslateWidget(Textarea):
    class Media:
        css = {
            'all': (
                'jquery-mentions-input/jquery.mentionsInput.css',
                'css/mentions.css'
            )
        }
        js = (
            'https://code.jquery.com/jquery-1.12.4.min.js',
            'mentions/js/underscore.min.js',
            'jquery-mentions-input/lib/jquery.elastic.js',
            'jquery-mentions-input/lib/jquery.events.input.js',
            'jquery-mentions-input/jquery.mentionsInput.js',
            'mentions/js/init.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {'class': 'mmention'}
        if attrs:
            default_attrs.update(attrs)

        super(TranslateWidget, self).__init__(default_attrs)

