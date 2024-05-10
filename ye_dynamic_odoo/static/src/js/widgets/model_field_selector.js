odoo.define('ye_dynamic_odoo.ModelFieldSelector', function (require) {
"use strict";

    var ModelFieldSelector = require('web.ModelFieldSelector');

    ModelFieldSelector.include({
        _hidePopover: function() {
            if ("editReport" in this.options && this._isOpen) {
                const {onChange} = this.options;
                if (onChange) {
                    onChange(this.chain.join("."));
                }
            }
            this._super();
        },
    });
});
