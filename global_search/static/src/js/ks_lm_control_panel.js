odoo.define("leadmaster.ks_lm_control_panel", function (require) {"use strict";

   var ControlPanel = require("web.ControlPanel"); //web.NavBar
   var { patch } = require("web.utils");
   var KsGlobalSearch = require("sh_global_search.GlobalSearch");
   var core = require("web.core");
   var QWeb = core.qweb;
   const { useListener } = require("web.custom_hooks");


    // todo: Patch the remaining methods from the below commented code
    patch(ControlPanel.prototype, "ks_lm_control_panel", {
        async setup(parent, menuData) {
            this._super();
            this.parent = parent;
        },

        mounted() {
            this._super();
            if ($(".o_action_manager").find(".ks_sh_search_results").length==0){
                $(".o_action").after('<div class="sh_search_results ks_sh_search_results col-md-12 ml-auto mr-auto"/>');
            }
            if ($(".sh_search_container").length){
                $($('.sh_search_container')[0].parentNode).addClass('ks_sh_global_search');
                if ($(".o_mail_navbar_item").length){
                    $(".o_mail_navbar_item").prependTo(".ks_sh_global_search").get(0);
                }
            }
            $(document).on('click', '.ks_close_result', function(event) {
                    $(".o_action_manager").find(".sh_search_results").empty();
                    $('.ks_sh_search_results')[0].classList.remove("has-results");
            });

            $(".usermenu_search_input").ready(function() {
                $('.usermenu_search_input').focus();
            });
            if ($(".ks_top_bar").length>0){
                $(".ks_lm_systray").prependTo(".ks_top_bar").get(0);
                $($('.o_main_navbar')[0].getElementsByClassName('o_menu_systray')[0]).empty();
            }
            else{
                $('.ks_lm_systray').addClass('d-none');
            }
            },

    });
});
