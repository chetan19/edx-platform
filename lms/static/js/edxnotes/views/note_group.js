;(function (define, undefined) {
'use strict';
define([
    'gettext', 'underscore', 'backbone'
], function (gettext, _, Backbone) {
    var NoteGroupView = Backbone.View.extend({
        tagName: 'section',
        className: 'note-group',
        id: function () {
            return 'note-group-' + _.uniqueId();
        },
        template: _.template([
            '<h3 class="group-lecture">',
                '<span class="course-title"><%- chapterName %></span>',
                '<span class="course-subtitle"><%- sectionName %></span>',
            '</h3>'
        ].join('')),

        initialize: function () {
            this.children = [];
        },

        render: function () {
            this.$el.html(this.template({
                chapterName: this.getChapterName(),
                sectionName: this.getSectionName()
            }));
            this.$el.append(this.children);

            return this;
        },

        getChapterName: function () {
            return this.options.chapter.display_name || '';
        },

        getSectionName: function () {
            return this.options.section.display_name || '';
        },

        addChild: function (child) {
            this.children.push(child);
        },

        remove: function () {
            this.children = null;
            Backbone.View.prototype.remove.call(this);
            return this;
        }
    });

    return NoteGroupView;
});
}).call(this, define || RequireJS.define);
