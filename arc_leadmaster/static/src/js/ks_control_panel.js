odoo.define("leadmaster.ks_control_panel", function (require) {"use strict";

   var ControlPanel = require("web.ControlPanel");
    var { patch } = require("web.utils");


    // todo: Patch the remaining methods from the below commented code
    patch(ControlPanel.prototype, "ks_control_panel", {

        mounted() {
            this._super();

            // Added Div for Top bar. Code add by Manmohan Singh
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
