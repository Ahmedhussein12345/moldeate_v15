odoo.define("global_search.KsGlobalSearch", function (require) {
    "use strict";

    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var core = require("web.core");
    var _t = core._t;
    var QWeb = core.qweb;
    var GlobalSearch = require("sh_global_search.GlobalSearch");
    var start_search_after_letter = 0;

    var KsGlobalSearch = GlobalSearch.GlobalSearch.include({
       events: {
            "keyup .sh_search_input input": "_ksOnSearchResultsNavigate",
            "click .ks_result_more": "_ksOnSearchResultsNavigate",
            "click .clear_Search": "ks_on_click_clear_Search",
        },

        init: function (parent) {
            this._super(parent);
        },

        // Inherit method for custom arguments. Code add by Manmohan Singh
        ks_linkInfo: function (key) {
            for (var k in this._searchableMenus) {
                if (!this._checkIsMenu(k)) {
                    var original = this._searchableMenus[k][key];
                    return original;
                }
            }

        },

        // Inherit method for custom arguments. Code add by Manmohan Singh
       _linkInfo: function (key) {
            var original = this._searchableMenus['search_result'][key];
            return original;
        },

        // Inherit method for custom arguments. Code add by Manmohan Singh
       _getFieldInfo: function (key) {
            let rec_list = []
            let value
            key = key.split("|")[1];
            if (key.includes(">")){
                key = key.split(">")[1];
            }
            value = key.split(":")[1];
//            key = key.split(":")[0];
            rec_list.push(key, value);
            return rec_list;
        },

        // Inherit method for return custom data. Code add by Manmohan Singh
        _searchData: function (event) {
            var keycode = (event.keyCode ? event.keyCode : event.which);
            var query = this.$(".sh_search_input input").val();
            if (query === "") {
                this.$(".sh_search_container").removeClass("has-results");
                this.$(".sh_search_results").empty();
                return;
            }
            var self = this;
            if ((query.length >= start_search_after_letter) && (keycode != '13')) {
                this._rpc({
                    model: "global.search",
                    method: "get_search_result",
                    args: [[query]],
                }).then(function (data) {
                    if (data) {
                        var rec_count = {}
                        for (let key in data.ks_menu_record) {
                            let count=0
                            for (let rec in data.ks_menu_record[key]) {
                                count++
                            }
                            rec_count[key] = count
                        }

                        self._searchableMenus = data;
                        var results = _.keys(self._searchableMenus['search_result']);
                        var icons = data['table_icon'];
                        self.$(".sh_search_results").toggleClass("has-results", Boolean(results.length));
                        self.$(".sh_search_results").html(QWeb.render("sh_global_search.MenuSearchResults", {
                                icons: icons,
                                results: results,
                                rec_count: rec_count,
                                widget: self,
                            })
                        );
                    }
                });
            }
            if ((query.length >= start_search_after_letter) && (keycode == '13'|| keycode == '1')) {
                this._rpc({
                    model: "global.search",
                    method: "ks_get_search_result",
                    args: [[query]],
                }).then(function (data) {
                    if (data) {
                        var key_list=[]
                        var rec_count = {}

                        for (let key in data.ks_menu_record) {
                            let count=0
                            for (let rec in data.ks_menu_record[key]) {
                                count++
                            }
                            rec_count[key] = count
                        }

                        var icons = data['table_icon'];
                        var records = data.ks_menu_record;
                        self._searchableMenus = data.search_result_menu;
                        var key_list = data.search_result_keys;
                        var remain_table = data.remain_table
                        var results = data.search_result;
                        var ks_menu = data.search_result_menu;
                        self.$(".sh_search_results").toggleClass("has-results", Boolean(results.length));
                    }

            // Added code for search result page records. Code add by Manmohan Singh
            var search_result_div=$(".o_action_manager").find(".sh_search_results")
            let ks_data_key;
            if(keycode == '13'|| keycode == '1'){
                var result_template=QWeb.render("global_search.ks_search_page",
                        {results: results,
                        ks_data_key:key_list,
                        ks_menu:ks_menu,
                        icons:icons,
                        rec_count: rec_count,
                        key_list:key_list,
                        records:records,
                        remain_table:remain_table,
                        widget: self,})
                    if (search_result_div[0]['children'].length){
                        search_result_div.empty();
                    }
                if ($(".ks_lm_systray").find(".sh_search_results").length){
                    $(".sh_search_results").empty();
                    $(".ks_lm_systray").find(".sh_search_input input").val('');
                }
                search_result_div.append(result_template);
            }
            if(keycode == '27'){
                $(".sh_search_input input").val('');
                $(".sh_search_results").empty();
            }
            if (search_result_div[0]['children'].length){
                    $('.ks_sh_search_results')[0].classList.add("has-results");
                }
            else{
                $('.ks_sh_search_results')[0].classList.remove("has-results");
            }
        //END
                });
        }

    },

    // Method for get records according search Character. Code add by Manmohan Singh
     _ksOnSearchResultsNavigate: function (event) {
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 500);
            this._search_def.done(this._searchData.bind(this,event));
            $(document).on('click', '.ks_search_result_tab', function(event) {
                var data_key = $(this).attr("data-key")
                var this_sibling = $($(this)[0]['parentNode'])[0]['children']
                var this_parent_sibling = $('.search_result_table')[0]['children']
                for (let s_key in this_sibling) {
                    let s_value;
                    // get the value
                    s_value = this_sibling[s_key];
                    if (typeof(s_value) == 'object'){
                        if ($(s_value).attr("data-key") == data_key){
                            $(s_value)[0].classList.add("selected");
                        }
                        else{
                            $(s_value)[0].classList.remove("selected");
                        }

                    }
                }
                for (let ps_key in this_parent_sibling) {
                    let ps_value;
                    // get the value
                    ps_value = this_parent_sibling[ps_key];
                    if (typeof(ps_value) == 'object'){
                        if ($(ps_value).attr("data-key") != data_key){
                            $(ps_value)[0].classList.add("o_hidden");
                        }
                        else{
                            $(ps_value)[0].classList.remove("o_hidden");
                        }
                    }
                }
            });
            return;
            },

    // For Clean Search bar. Code add by Manmohan Singh
    ks_on_click_clear_Search: function (ev) {
        this.$(".sh_search_input input").val('');
        this.$(".sh_search_results").empty();
        var keycode = (event.keyCode ? event.keyCode : event.which);
    },

    });
});
