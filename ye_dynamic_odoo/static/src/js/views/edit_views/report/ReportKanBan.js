odoo.define('ye_dynamic_odoo.ReportKanBan', function (require) {
"use strict";

    var core = require('web.core');
    var KanbanRenderer = require('web.KanbanRenderer');
    var KanbanView = require('web.KanbanView');
    var KanbanController = require('web.KanbanController');
    var KanbanRecord = require('web.KanbanRecord');


    var KanBanContentRecord = KanbanRecord.extend({
        init: function (parent, state, options) {
            this._super(parent, state, options);
            this.props = options;
        },
        _onGlobalClick: function (ev) {
            const {onClickRecord} = this.props;
            if (onClickRecord) {
                onClickRecord(this.state.data);
            }else {
                this._super(ev);
            }
        },
    });

    var KanBanContentRenderer = KanbanRenderer.extend({
        config: _.extend({}, KanbanRenderer.prototype.config, {
            KanbanRecord: KanBanContentRecord,
        }),
        init: function (parent, state, params) {
            this._super(parent, state, params);
            const {onClickRecord} = parent;
            this.recordOptions.onClickRecord = onClickRecord.bind(parent);
        },
    });

    var KanBanContentController = KanbanController.extend({
        _pushState: function () {
        }
    });

    var KanBanContentView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Renderer: KanBanContentRenderer,
            Controller: KanBanContentController,
        }),
        init: function (viewInfo, params) {
            this._super(viewInfo, params);
            this.props = params;
            this.config.Renderer = KanBanContentRenderer;
        }
    });

    return KanBanContentView;

});
