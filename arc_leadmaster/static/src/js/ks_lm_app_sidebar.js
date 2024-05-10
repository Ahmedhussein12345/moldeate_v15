odoo.define("leadmaster.ks_lm_app_sidebar", function (require) {"use strict";

   var LeftSideBar = require("ks_curved_backend_theme.ks_app_sidebar");
   var { patch } = require("web.utils");


    // todo: Patch the remaining methods from the below commented code
    patch(LeftSideBar.prototype, "ks_lm_app_sidebar", {

    start: function () {
    // Add if condition for remove left side bar panel. Code add by Manmohan Singh
      return this._super.apply(this, arguments).then(function () {
            if (($('.ks_horizontal_bar').length) && ($('.ks_app_sidebar_menu').length==0)){
                $('.ks_left_sidebar_panel').addClass('d-none');
            }
      });
    },

    });
});