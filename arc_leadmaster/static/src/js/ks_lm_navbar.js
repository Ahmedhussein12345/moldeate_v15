odoo.define("ks_curved_backend_theme.ks_lm_navbar",function (require) {"use strict";

    var { NavBar } = require("@web/webclient/navbar/navbar");
    var { patch } = require("web.utils");
    const { useListener } = require("web.custom_hooks");

    // todo: Patch the remaining methods from the below commented code
    patch(NavBar.prototype, "ks_lm_navbar", {
      async setup(parent, menuData) {
        useListener("click", "#ks_app_drawer_toggle", this._lmksAppsDrawerClick);
        useListener( "click", ".ks_o_apps a", this._lmksAppsDrawerClick);
        useListener( "click", ".ks_o_menuitems a", this._lmksAppsDrawerClick);
        useListener( "click", ".ks_appdrawer_inner_app_div .dropdown-item a", this._lmksAppsDrawerClick);
        useListener( "click", ".ks_appdrawer_inner_app_div a", this._lmksAppsDrawerClick);
        return this._super.apply(this, arguments);
      },

      mounted() {
        this._super();

        if ($(".ks_top_bar").length==0){
            const div = document.createElement("div");
            div.setAttribute("class", "ks_top_bar");
            const node = document.createElement("div");
            node.setAttribute("class", "ks_lm_logo");
            div.appendChild(node);

            $(".o_web_client").get(0).appendChild(div);
            $(".brand_logo").prependTo(node);
        }

        if ($(".o_web_client").hasClass("ks_vertical_body_panel")){
            $('.ks_top_bar').remove();
            $('.ks_lm_systray').remove();
        }

        if ($(".ks_top_bar").length>0){
            $(".ks_lm_systray").prependTo(".ks_top_bar").get(0);
            $($('.o_main_navbar')[0].getElementsByClassName('o_menu_systray')[0]).empty();
        }
        else{
            $('.ks_lm_systray').addClass('d-none');
        }

        if ($(".o_action_manager").find(".ks_sh_search_results").length==0){
            const search_node = document.createElement("div");
            search_node.setAttribute("class", "sh_search_results ks_sh_search_results col-md-12 ml-auto mr-auto");
            const search_textnode = document.createTextNode("");
            search_node.appendChild(search_textnode);
            $(".o_action_manager").get(0).appendChild(search_node);
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

      if ($(".right-sidebar-inner").length>1){
            $('.right-sidebar-inner')[1].remove();
      }

      $(".o_studio").ready(function() {
          $(".fa-expand").bind("click", function() {
            if ($(".ks_top_bar").hasClass("d-none")){
                $('.ks_top_bar').removeClass('d-none');
            }
            else{
                $('.ks_top_bar').addClass('d-none');
            }
          });
        });

      },


    // Add event on app drawer for adding or removing Top Bar. Code add by Manmohan Singh
    _lmksAppsDrawerClick(event){
       if (document.body.classList.contains("ks_appsmenu_active")) {
           if ($(".ks_top_bar").length>0){
                $('.ks_top_bar')[0].classList.remove('d-none');
            }
        }
        else {
           if ($(".ks_top_bar").length>0){
                $('.ks_top_bar')[0].classList.add('d-none');
            }
        }
       if ($(".o_studio").length){
            location.reload();
       }
      },


    });
});
