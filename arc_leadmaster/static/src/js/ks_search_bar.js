/** @odoo-module */
//search for graph and pivot view
var { SearchBar } = require("@web/search/search_bar/search_bar");
import { patch } from 'web.utils';


patch(SearchBar.prototype, 'ks_search_bar.js', {
    mounted() {
        if ($(".ks_top_bar").length>0){
            $(".ks_lm_systray").prependTo(".ks_top_bar").get(0);
        }
        else{
            $('.ks_lm_systray').addClass('d-none');
        }
    }
});
