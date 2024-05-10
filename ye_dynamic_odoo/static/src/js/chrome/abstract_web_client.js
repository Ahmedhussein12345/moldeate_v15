odoo.define('ye_dynamic_odoo.AbstractWebClient', function (require) {
"use strict";

    var WebClient = require('web.WebClient');

    WebClient.include({
        custom_events: _.extend({}, WebClient.prototype.custom_events, {
            reset_edit_instance: 'resetEditInstance',
        }),
        resetEditInstance: function () {
            if (this.editInstance) {
                delete this.loadEdit;
                delete this.editInstance;
            }
        },
        on_menu_clicked: function (ev) {
            if (this.editInstance) {
                this.loadEdit = true;
            }
            this._super(ev);
        },
//        _on_app_clicked_done: function (ev) {
//            if (this.editInstance) {
//                this.loadEdit = true;
//            }
//            return this._super(ev);
//        },
        on_app_clicked: function (ev) {
            if (this.editInstance) {
                this.loadEdit = true;
            }
            return this._super(ev);
        },
        do_push_state: function (state) {
            this._super(state);
            if (this.editInstance) {
                const {model} = this.editInstance.appState, state = odoo.studio.state;
                if (this.loadEdit || model != state.model) {
                    delete this.loadEdit;
                    this.editInstance.reload(this);
                }
            }
        },
    });
});
