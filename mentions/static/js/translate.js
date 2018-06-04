jQuery(function ($) {

    'use strict';

    function translateArea() {
        // language=JQuery-CSS

        $.getJSON('/nouns/?' + Math.random(), function(data) {
            var mentions = $('.mentions');

            mentions.mentionsInput({
                source: data,
                showAtCaret: true
            });

            mentions.each(function (idx, mention) {
                var item = $(mention);

                item.parents('form').on('submit', function () {
                    item.val(item.mentionsInput('getValue'));
                })
            });
        });

    }

    //Init function in the view
    translateArea();


});