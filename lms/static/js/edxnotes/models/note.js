;(function (define) {
'use strict';
define(['backbone', 'underscore.string'], function (Backbone) {
    var NoteModel = Backbone.Model.extend({
        defaults: {
            'id': null,
            'created': null,
            'updated': null,
            'user': null,
            'usage_id': null,
            'course_id': null,
            'text': null,
            'quote': '',
            'unit': {
                'display_name': null,
                'url': null
            },
            'ranges': [],
            'is_expanded': false,
            'show_link': false
        },

        textSize: 300,

        initialize: function () {
            if (this.escape('quote').length > this.textSize) {
                this.set('show_link', true);
            }
        },

        getNoteText: function () {
            var message = this.escape('quote');

            if (!this.get('is_expanded') && this.get('show_link')) {
                message = _.str.prune(message, this.textSize);
            }

            return message;
        }

    });

    return NoteModel;
});
}).call(this, define || RequireJS.define);
