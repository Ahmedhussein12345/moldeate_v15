odoo.define('ye_dynamic_odoo.AbstractController', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractController = require('web.AbstractController');
    var AbstractView = require('web.AbstractView');
    var EditView = require('ye_dynamic_odoo.EditView');
    var startStudio = require("ye_dynamic_odoo.Start");
    // var StudioEditor = require("ye_dynamic_odoo.StudioEditor");
    var { ControlPanel } = require("@web/search/control_panel/control_panel");
    var {session} = require("@web/session");
    var QWeb = core.qweb;
    const {Component} = owl;

    class StudioIcon extends Component {
        setup() {
            this.isShow = session['showEdit'];
        }
        onClickIconStudio() {
            startStudio(this.env);
        }
    }

    StudioIcon.components = {};
    StudioIcon.template = "studio.StudioIcon";
    ControlPanel.components = Object.assign(ControlPanel.components, {StudioIcon: StudioIcon});


    AbstractController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.fieldsView = params.fieldsView || {};
            this._processFieldsView = params._processFieldsView || false;
        },
        start: async function () {
            await this._super(this);
            const env = this.ControlPanel && this.ControlPanel.env;
            this.$el.find(".o_edit").css({display: "none"});
            if (this._controlPanelWrapper && !odoo.studio) {
                // const webClient = this.getParent().getParent();
                let session_legacy = this.getSession() || {};
                // this.$el.find(".o_edit").css({display: "none"})
                if (session_legacy['showEdit']) {
                    this.$el.find(".o_edit").css({display: "block"});
                    this.$el.find(".o_edit").click(() => {
                        startStudio(env);

                        // this.getParent().$el.after(newView.$el);
                    });
                }
            }
        },
        _pushState: function () {
            if (this.fromEdit) {
                return true;
            }
            this._super();
        },
        // _renderSwitchButtons: function () {
        //     let res = this._super();
        //     let session = this.getSession() || {};
        //     if (session['showEdit']) {
        //         this._renderEditMode(res);
        //     }
        //     return res;
        // },
        _renderEditMode: function (container) {
            const $editMode = $(QWeb.render("EditView.iconMore", this)),
                webClient = this.getParent().getParent();
            container.push($editMode[0]);
            $editMode.click(() => {
                let newView = new EditView(this, {modelName: this.modelName});
                newView.renderElement();
                webClient.editInstance = newView;
                this.getParent().$el.after(newView.$el);
            });
        }
    });

    AbstractView.include({
        init: function (viewInfo, params) {
            this._super(viewInfo, params);
            this.controllerParams.fieldsView = this.fieldsView;
            this.controllerParams._processFieldsView = this._processFieldsView.bind(this);
        }
    });
});
