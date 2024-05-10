odoo.define("leadmaster.ks_top_bar", function (require) {"use strict";

    var config = require("web.config");
    // To check the device

    var { WebClient } = require("@web/webclient/webclient");
    var { patch } = require("web.utils");
    var KsGlobalSearch = require("sh_global_search.GlobalSearch");

    // todo: Patch the remaining methods from the below commented code
    patch(WebClient.prototype, "ks_top_bar", {
        mounted() {
            // the chat window and dialog services listen to 'web_client_ready' event in
            // order to initialize themselves:
//            this.env.bus.trigger("WEB_CLIENT_READY");
            this._super();
            const div = document.createElement("div");
            div.setAttribute("class", "ks_top_bar");
            const node = document.createTextNode("");
            div.appendChild(node);

            $(".o_web_client").get(0).appendChild(div);
//            var test = new KsGlobalSearch.GlobalSearch();
//            test.prependTo(div);
            $(".brand_logo").prependTo(div);
            if ($(".o_web_client").hasClass("ks_vertical_body_panel")){
                $('.ks_top_bar').remove();
                $('.ks_lm_systray').remove();
            }

        }
    });
});