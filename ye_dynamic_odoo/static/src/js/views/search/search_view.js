odoo.define('ye_dynamic_odoo.search_view', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractController = require('web.AbstractController');

    AbstractController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            parent.searchview = this;
        },
        _onSearch: function (searchQuery) {
            if (this.listViewRender) {
                var domains = this.listViewRender._prepareSearchDomains();
                if (searchQuery.domain.length >= 1) {
                    searchQuery.domain = searchQuery.domain.concat(domains);
                }else {
                    searchQuery.domain = domains;
                }
            }
            this._super(searchQuery);
        }
    });
});
