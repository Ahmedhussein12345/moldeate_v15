odoo.define('ye_dynamic_odoo.jquery.extensions', function () {
'use strict';

    // jQuery functions extensions
    var propRowIndex = $.fn.prop;
    $.fn.extend({
        prop: function( name, value ) {
            let result = propRowIndex.apply(this, arguments);
            if (name === "rowIndex") {
                var tableCheck = this.parents(".o_list_table");
                if (tableCheck.length) {
                    let advanceSearch = tableCheck.find(".searchAdvance").length ? 1 : 0,
                        sticky = tableCheck.find(".tableFloatingHeader").length ? 1 : 0;
                    if (advanceSearch && sticky) {
                        result -= 3;
                    }else {
                        if (advanceSearch || sticky) {
                            result -= 1;
                        }
                    }
                }
            }
            return result;
        },
    });
});
