odoo.define("global_search.ks_global_app_include", function(require) {"use strict";

    var KsGlobalSearch = require("sh_global_search.GlobalSearch");

//    var lm_global_search = KsGlobalSearch.GlobalSearch.include({
//    start: function(){
//     this._super.apply(this, arguments);
//        alert('hi');
//    }
//});
    var lm_global_search = KsGlobalSearch.GlobalSearch.extend({
        events: _.extend({}, KsGlobalSearch.GlobalSearch.prototype.events, {
            "keydown .ks_top_bar .sh_search_input input": "_ksonSearchResultsNavigate",
//            "keydown .ks_top_bar .sh_search_input input": "_onSearchResultsNavigate",
        }),

        _ksonSearchResultsNavigate: function (event) {
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 500);
            this._search_def.done(this._searchData.bind(this));
            return;
        },


    });

    $(function () {
            // TODO move this to another module, requiring dom_ready and rejecting
            // the returned deferred to get the proper message
    $('.sh_search_container').each(function () {
    alert('gii');
    })
            });

});
