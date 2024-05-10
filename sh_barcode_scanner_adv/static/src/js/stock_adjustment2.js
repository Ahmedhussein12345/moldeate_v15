/** @odoo-module alias=sh_barcode_scanner.stock_adjustment2 **/

/**
 * Editable List renderer
 *
 * The list renderer is reasonably complex, so we split it in two files. This
 * file simply 'includes' the basic ListRenderer to add all the necessary
 * behaviors to enable editing records.
 *
 * Unlike Odoo v10 and before, this list renderer is independant from the form
 * view. It uses the same widgets, but the code is totally stand alone.
 */
import core from 'web.core';
import dom from 'web.dom';
import ListRenderer from 'web.ListRenderer';
import utils from 'web.utils';
import { WidgetAdapterMixin } from 'web.OwlCompatibility';

var QWeb = core.qweb;
const session = require('web.session');
var Dialog = require('web.Dialog');

var _t = core._t;

var rpc = require('web.rpc');

ListRenderer.include({
    events: _.extend({}, ListRenderer.prototype.events, {
        'change .js_cls_sh_barcode_scanner_stock_quant_tree_input_barcode': '_on_change_sh_barcode_scanner_stock_quant_tree_input_barcode',
        'click .js_cls_sh_barcode_scanner_stock_quant_tree_btn_apply': '_on_click_js_cls_sh_barcode_scanner_stock_quant_tree_btn_apply',
        'change .js_cls_sh_barcode_scanner_location_select': '_on_change_sh_barcode_scanner_location_select',
        'change .scan_negative_stock_cls': 'on_change_scan_negative_stock_cls',

    }),
    /**
     * @override
     * @param {Object} params
     * @param {boolean} params.addCreateLine
     * @param {boolean} params.addCreateLineInGroups
     * @param {boolean} params.addTrashIcon
     * @param {boolean} params.isMany2Many
     * @param {boolean} params.isMultiEditable
     */
    init: function(parent, state, params) {
        this._super.apply(this, arguments);
    },


    /**
     * Instantiates the widget_data from backend like location, stock manager and so on.
     *
     * @override
     * @returns {Promise}
     */
    willStart: async function() {
        var self = this;
        const _super = this._super.bind(this, ...arguments);
        await self._sh_barcode_scanner_load_widget_data();
        var def1 = _super();
        return Promise.all([def1]);
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    _sh_barcode_scanner_load_widget_data: async function() {
        var self = this;
        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_get_widget_data', {});
        self.sh_barcode_scanner_user_is_stock_manager = result.user_is_stock_manager;
        self.sh_barcode_scanner_user_has_stock_multi_locations = result.user_has_stock_multi_locations;
        self.sh_barcode_scanner_locations = result.locations;
        self.sh_inven_adjt_barcode_scanner_auto_close_popup = result.sh_inven_adjt_barcode_scanner_auto_close_popup;
        self.sh_inven_adjt_barcode_scanner_warn_sound = result.sh_inven_adjt_barcode_scanner_warn_sound;

        self.sh_barcode_scanner_location_selected = localStorage.getItem('sh_barcode_scanner_location_selected') || '';
        self.sh_scan_negative_stock = localStorage.getItem('sh_barcode_scanner_is_scan_negative_stock') || '';


    },



    /**
     * @override
     * @private
     * @returns {Promise} this promise is resolved immediately
     */
    _renderView: function() {
        this.currentRow = null;
        var self = this;
        return this._super.apply(this, arguments).then(() => {
            var model = '';
            if (self.state && self.state.model) {
                model = self.state.model || '';
            }
            if (model == 'stock.quant') {
                var content_scanner = QWeb.render('sh_barcode_scanner.stock_adjustment.tree.scan_feature', {
                    'widget': self,

                })
                self.$el.prepend(content_scanner);
            }


        });
    },



    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * This method is called when barcode is changed above tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_change_sh_barcode_scanner_stock_quant_tree_input_barcode: async function(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var self = this;
        var barcode = $(ev.currentTarget).val();
        var location_id = false;
        var scan_negative_stock = false;
        var location_name = '';
        var scan_negative_stock = $(ev.currentTarget).closest('.js_cls_sh_barcode_scanner_scanning_wrapper').find('.scan_negative_stock_cls').prop('checked');
        var $location_select = $(ev.currentTarget).closest('.js_cls_sh_barcode_scanner_scanning_wrapper').find('.js_cls_sh_barcode_scanner_location_select');
        if ($location_select.length) {
            location_id = $location_select.val();
            location_name = $location_select.find("option:selected").text();
        }
        if (location_id) {
            location_id = parseInt(location_id);
        }

        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_search_stock_quant_by_barcode', {
            'barcode': barcode,
            'location_id': location_id,
            'location_name': location_name,
            'scan_negative_stock': scan_negative_stock,
        });
        if (result.result) {
            self.trigger_up('reload');
        } else {
            var message = _t(result.message);
            var dialog = new Dialog(this, {
                title: _t("Something went wrong"),
                $content: $('<p>' + message + '</p>')
            });
            dialog.open();

            // auto close dialog.
            if (self.sh_inven_adjt_barcode_scanner_auto_close_popup > 0) {
                setTimeout(function() {
                    if (dialog) {
                        dialog.close();
                    }
                }, self.sh_inven_adjt_barcode_scanner_auto_close_popup);
            }
            // Play Warning Sound
            if (self.sh_inven_adjt_barcode_scanner_warn_sound) {
                var src = "/sh_inventory_adjustment_barcode_scanner/static/src/sounds/error.wav";
                $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
            }

        }

    },




    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * This method is called when barcode is changed above the tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_click_js_cls_sh_barcode_scanner_stock_quant_tree_btn_apply: async function(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var self = this;
        const result = await session.rpc('/sh_barcode_scanner/sh_barcode_scanner_stock_quant_tree_btn_apply', {});
        var error = false;
        var title = _t("Something went wrong");
        if (result.result) {
            title = _t("Inventory Succeed");
            self.trigger_up('reload');
        } else {
            title = _t("Something went wrong");
            error = true;
        }
        var message = _t(result.message);
        var dialog = new Dialog(this, {
            title: title,
            $content: $('<p>' + message + '</p>')
        });
        dialog.open();

        // auto close dialog.
        if (error && self.sh_inven_adjt_barcode_scanner_auto_close_popup > 0) {
            setTimeout(function() {
                if (dialog) {
                    dialog.close();
                }
            }, self.sh_inven_adjt_barcode_scanner_auto_close_popup);
        }
        // Play Warning Sound
        if (error && self.sh_inven_adjt_barcode_scanner_warn_sound) {
            var src = "/sh_inventory_adjustment_barcode_scanner/static/src/sounds/error.wav";
            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
        }


    },


    /**
     * This method is called when location is changed above tree view
     * list view.
     *
     * @param {MouseEvent} ev
     */
    _on_change_sh_barcode_scanner_location_select: async function(ev) {
        ev.stopPropagation();
        var location = $(ev.currentTarget).val();
        localStorage.setItem('sh_barcode_scanner_location_selected', location);
    },

    on_change_scan_negative_stock_cls: async function(ev) {
        ev.stopPropagation();
        var self = this;
        var scan_negative_stock = $(ev.currentTarget).prop('checked');
        if (scan_negative_stock) {
            scan_negative_stock = 'true';
        } else {
            scan_negative_stock = 'false';
        }
        self.sh_scan_negative_stock = scan_negative_stock;
        localStorage.setItem('sh_barcode_scanner_is_scan_negative_stock', scan_negative_stock);

    },



});