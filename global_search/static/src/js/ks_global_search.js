odoo.define("leadmaster.ks_global_search", function (require) {"use strict";

    var config = require("web.config");
    // To check the device

    var { WebClient } = require("@web/webclient/webclient");
    var { patch } = require("web.utils");
    var core = require("web.core");
    var QWeb = core.qweb;

    // todo: Patch the remaining methods from the below commented code
    patch(WebClient.prototype, "ks_global_search", {
        mounted() {
            // the chat window and dialog services listen to 'web_client_ready' event in
            // order to initialize themselves:
            this._super();
            if ($(".ks_top_bar").length>0){
//                if ($('.ks_top_bar')[0].getElementsByClassName('sh_search_container').length==0){
//                    $(".sh_search_container").prependTo(".ks_top_bar").get(0);
//                }
//                const div = document.createElement("div");
//                div.setAttribute("class", "ks_search_bar");
//                const node = document.createElement("input");
//                const search = document.createTextNode("");
//                node.setAttribute("class", "usermenu_search_input form-control");
//                node.setAttribute("placeholder", "Search ...");
//                node.setAttribute("type", "text");
//                node.appendChild(search);
//                div.appendChild(node);
//                  $(".ks_top_bar").append(QWeb.render("test"));
console.log('aaaa')
//                $(".ks_top_bar").get(0).appendChild(div);
            }
            else{
                $('.ks_lm_systray').addClass('d-none');
            }
        }
    });
});