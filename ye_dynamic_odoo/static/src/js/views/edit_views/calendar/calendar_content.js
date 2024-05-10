odoo.define('ye_dynamic_odoo.CalendarViewContent', function (require) {
    "use strict";

    var core = require('web.core');
    var CalendarView = require('web.CalendarView');
    var CalendarController = require('web.CalendarController');

    var Base = require('ye_dynamic_odoo.BaseEdit');
    var {ViewContainer} = require('ye_dynamic_odoo.ViewContainer');
    const {mount} = owl;
    //
    // CalendarController.include({
    //     init: function (parent, model, renderer, params) {
    //         this._super(parent, model, renderer, params);
    //         this.props = params;
    //     },
    //     _pushState: function () {
    //         const {fromEdit} = this.props;
    //         if (!fromEdit) {
    //             this._super();
    //         }
    //     }
    // });

    var FormEditContent = Base.ContentBase.extend({
        template: 'CalendarViewEdit.Content',
        init: function (parent, params) {
            this._super(parent, params);
            this.parent = parent;
        },
        start: function () {
            const {action} = this.props;
            this.action = action;
        },
        bindAction: function () {
        },
        renderView: async function () {
            let self = this;
            const {context, domain, limit, res_model, filter} = this.action, {viewInfo} = this.props;
            let params = {
                action: this.action,
                context: context,
                domain: domain || [],
                groupBy: [],
                limit: limit,
                filter: filter || [],
                modelName: res_model,
                withControlPanel: false,
                withSearchPanel: false,
            };

            const info = {
                View: CalendarView,
                viewInfo: viewInfo,
                viewParams: params
            }
            const env = odoo.rootStudio.env;
            await mount(ViewContainer, {
                env,
                props: {info: info, isLegacy: true},
                target: self.$el[0],
                position: "first-child"
            });
        },
    });

    return FormEditContent;

});
