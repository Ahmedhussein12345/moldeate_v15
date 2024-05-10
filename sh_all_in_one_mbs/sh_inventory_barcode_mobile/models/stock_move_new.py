# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api,  _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    sh_stock_move_barcode_mobile = fields.Char(string="Mobile Barcode")

    @api.model
    def default_sh_stock_move_bm_is_cont_scan(self):
        return self.env.company.sh_stock_bm_is_cont_scan

    sh_stock_move_bm_is_cont_scan = fields.Char(
        string='Continuously Scan?',
        default=default_sh_stock_move_bm_is_cont_scan,
        readonly=True)

    def sh_stock_move_barcode_mobile_no_tracking(self, barcode, CODE_SOUND_SUCCESS,
                                                 CODE_SOUND_FAIL):
        # move_lines = False
        #
        # # INCOMING
        # # ===================================
        # if self.picking_code in ['incoming']:
        #     move_lines = self.move_line_nosuggest_ids
        #
        # # OUTGOING AND TRANSFER
        # # ===================================
        # elif self.picking_code in ['outgoing', 'internal']:
        #     move_lines = self.move_line_ids

        # 15.0.3
        move_lines = self._get_move_lines()
        # 15.0.3
        # UPDATED CODE

        if move_lines:
            for line in move_lines:
                if self.env.company.sudo(
                ).sh_stock_barcode_mobile_type == 'barcode':
                    if self.product_id.barcode == barcode:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        if self.picking_code in ['incoming']:
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, {
                                    'qty_done':
                                    qty_done
                                })]
                            })
                        if self.picking_code in ['outgoing', 'internal']:
                            self.update({
                                'move_line_ids': [(1, line.id, {
                                    'qty_done': qty_done
                                })]
                            })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s') % (
                                            self.product_id.name,
                                            qty_done)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        if self.quantity_done == self.product_uom_qty + 1:
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    'Becareful! Quantity exceed than initial demand!'
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Alert"),
                                        'message': message,
                                    })

                        break
                    else:
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Scanned Internal Reference/Barcode not exist in any product!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })
                        return

                elif self.env.company.sudo(
                ).sh_stock_barcode_mobile_type == 'int_ref':
                    if self.product_id.default_code == barcode:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        if self.picking_code in ['incoming']:
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, {
                                    'qty_done':
                                    qty_done
                                })]
                            })
                        if self.picking_code in ['outgoing', 'internal']:
                            self.update({
                                'move_line_ids': [(1, line.id, {
                                    'qty_done': qty_done
                                })]
                            })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s') % (
                                            self.product_id.name,
                                            qty_done)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        if self.quantity_done == self.product_uom_qty + 1:
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    'Becareful! Quantity exceed than initial demand!'
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Alert"),
                                        'message': message,
                                    })

                        break
                    else:
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Scanned Internal Reference/Barcode not exist in any product!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })

                        return

                elif self.env.company.sudo(
                ).sh_stock_barcode_mobile_type == 'sh_qr_code':
                    if self.product_id.sh_qr_code == barcode:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        if self.picking_code in ['incoming']:
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, {
                                    'qty_done':
                                    qty_done
                                })]
                            })
                        if self.picking_code in ['outgoing', 'internal']:
                            self.update({
                                'move_line_ids': [(1, line.id, {
                                    'qty_done': qty_done
                                })]
                            })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s') % (
                                            self.product_id.name,
                                            qty_done)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        if self.quantity_done == self.product_uom_qty + 1:
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    'Becareful! Quantity exceed than initial demand!'
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Alert"),
                                        'message': message,
                                    })

                        break
                    else:
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Scanned Internal Reference/Barcode not exist in any product!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        return

                elif self.env.company.sudo(
                ).sh_stock_barcode_mobile_type == 'all':

                    if self.product_id.barcode == barcode or self.product_id.default_code == barcode or self.product_id.sh_qr_code == barcode:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        if self.picking_code in ['incoming']:
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, {
                                    'qty_done':
                                    qty_done
                                })]
                            })
                        if self.picking_code in ['outgoing', 'internal']:
                            self.update({
                                'move_line_ids': [(1, line.id, {
                                    'qty_done': qty_done
                                })]
                            })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s') % (
                                            self.product_id.name,
                                            qty_done)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        if self.quantity_done == self.product_uom_qty + 1:
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    'Becareful! Quantity exceed than initial demand!'
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Alert"),
                                        'message': message,
                                    })

                        break
                    else:
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Scanned Internal Reference/Barcode not exist in any product!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })

                        return

        else:
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL +
                            'Pls add all product items in line than rescan.')
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })

            return



    @api.onchange('sh_stock_move_barcode_mobile')
    def _onchange_sh_stock_move_barcode_mobile(self):

        if self.sh_stock_move_barcode_mobile in ['', "", False, None]:
            return

        CODE_SOUND_SUCCESS = ""
        CODE_SOUND_FAIL = ""
        if self.env.company.sudo().sh_stock_bm_is_sound_on_success:
            CODE_SOUND_SUCCESS = "SH_BARCODE_MOBILE_SUCCESS_"

        if self.env.company.sudo().sh_stock_bm_is_sound_on_fail:
            CODE_SOUND_FAIL = "SH_BARCODE_MOBILE_FAIL_"

        if self.picking_id.state not in ['confirmed', 'assigned']:
            selections = self.picking_id.fields_get()['state']['selection']
            value = next(
                (v[1] for v in selections if v[0] == self.picking_id.state),
                self.picking_id.state)
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL +
                            'You can not scan item in %s state.') % (value)
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })

            return


        show_lots_m2o = self.has_tracking != 'none' and (
            self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id)
        show_lots_text = self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id

        res = {}
        barcode = self.sh_stock_move_barcode_mobile
        if show_lots_m2o:
            res = self.sh_stock_move_barcode_mobile_has_tracking_show_lots_m2o(
                barcode, CODE_SOUND_SUCCESS, CODE_SOUND_FAIL)
        elif show_lots_text:
            res = self.sh_stock_move_barcode_mobile_has_tracking_show_lots_text(
                barcode, CODE_SOUND_SUCCESS, CODE_SOUND_FAIL)
        else:
            res = self.sh_stock_move_barcode_mobile_no_tracking(
                barcode, CODE_SOUND_SUCCESS, CODE_SOUND_FAIL)
        return res


        # if self.sh_stock_move_barcode_mobile:
        #     if self.has_tracking != 'none':
        #         self.sh_stock_move_barcode_mobile_has_tracking(
        #             CODE_SOUND_SUCCESS, CODE_SOUND_FAIL)

        #     else:
        #         self.sh_stock_move_barcode_mobile_no_tracking(
        #             CODE_SOUND_SUCCESS, CODE_SOUND_FAIL)



    # def on_barcode_scanned(self, barcode):
    #     is_last_scanned = False
    #     sequence = 0
    #     warm_sound_code = ""

    #     if self.env.company.sudo().sh_inventory_barcode_scanner_last_scanned_color:
    #         is_last_scanned = True

    #     if self.env.company.sudo().sh_inventory_barcode_scanner_move_to_top:
    #         sequence = -1

    #     if self.env.company.sudo().sh_inventory_barcode_scanner_warn_sound:
    #         warm_sound_code = "SH_BARCODE_SCANNER_"

    #     if self.env.company.sudo().sh_inventory_barcode_scanner_auto_close_popup:
    #         warm_sound_code += "AUTO_CLOSE_AFTER_" + \
    #             str(self.env.company.sudo(
    #             ).sh_inventory_barcode_scanner_auto_close_popup) + "_MS&"

    #     # UPDATED CODE
    #     # =============================
    #     if self.picking_id.state not in ["confirmed", "assigned"]:
    #         selections = self.picking_id.fields_get()["state"]["selection"]
    #         value = next((v[1] for v in selections if v[0] ==
    #                       self.picking_id.state), self.picking_id.state)
    #         raise UserError(
    #             _(warm_sound_code + "You can not scan item in %s state.") % (value))

    #     # if self.has_tracking != 'none':
    #     #     # LOT / SERIAL FLOW
    #     #     self.sh_stock_move_barcode_scanner_has_tracking(
    #     #         barcode, sequence, is_last_scanned, warm_sound_code)
    #     # else:
    #     #     # NORMAL PRODUCT FLOW
    #     #     self.sh_stock_move_barcode_scanner_no_tracking(
    #     #         barcode, sequence, is_last_scanned, warm_sound_code)

    #     # -----------------------------
    #     # sh_auto_serial_scanner
    #     # -----------------------------
    #     show_lots_m2o = self.has_tracking != 'none' and (
    #         self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id)
    #     show_lots_text = self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id

    #     res = {}
    #     if show_lots_m2o:
    #         res = self.sh_stock_move_barcode_mobile_has_tracking_show_lots_m2o(
    #             barcode, sequence, is_last_scanned, warm_sound_code)
    #     elif show_lots_text:
    #         res = self.sh_stock_move_barcode_mobile_has_tracking_show_lots_text(
    #             barcode, sequence, is_last_scanned, warm_sound_code)
    #     else:
    #         res = self.sh_stock_move_barcode_mobile_no_tracking(
    #             barcode, sequence, is_last_scanned, warm_sound_code)
    #     return res

    def sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(self, lot_name, product_id, CODE_SOUND_FAIL):
        """
            Search or Create lot number
            @param: lot_name - search record based given lot name.
            @param: product_id - Integer -  search record based given product_id.
            @return: lot object
        """
        # able to create lots, whatever the value of ` use_create_lots`.

        # Search or create lot/serial number
        lot = self.env['stock.production.lot'].search([
            ('name', '=', lot_name),
            ('product_id', '=',
                product_id),
            ('company_id', '=',
                self.env.company.id)
        ], limit=1)
        if not lot:
            lot = self.env['stock.production.lot'].create({
                'name': lot_name,
                'product_id': product_id,
                # 'product_qty': move_line_vals['qty_done'],
                'company_id': self.env.company.id,
            })

        if not lot:
            raise UserError(
                _("Can't create Lots/Serial Number record for this lot/serial. % s") % (lot_name))

        return lot

    def sh_stock_move_barcode_mobile_has_tracking_show_lots_m2o(self, barcode, CODE_SOUND_SUCCESS, CODE_SOUND_FAIL):
        # self.picking_id.show_lots_text
        if self.picking_code == 'incoming':
            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: not r.lot_id)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, CODE_SOUND_FAIL)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })

                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s Lot: %s') % (
                                                self.product_id.display_name,
                                                qty_done, barcode)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })                            
                            break

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [barcode])
                        for move_line_command in move_lines_commands:
                            move_line_vals = move_line_command[2]
                            lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                                barcode, self.product_id.id, CODE_SOUND_FAIL)
                            move_line_vals['lot_id'] = lot.id
                        self.update({
                            'move_line_nosuggest_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  
            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.production.lot'].generate_lot_names(
                #     barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    # raise UserError(
                    #     _(warm_sound_code + "Serial Number already exist!"))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL +
                            'Serial Number already exist!'
                        )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: not r.lot_id)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        #qty_done = line.qty_done + 1
                        qty_done = 1
                        lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, CODE_SOUND_FAIL)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

                        break
                else:
                    move_lines_commands = self._generate_serial_move_line_commands(
                        [barcode])

                    for move_line_command in move_lines_commands:
                        move_line_vals = move_line_command[2]
                        lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, CODE_SOUND_FAIL)
                        move_line_vals['lot_id'] = lot.id
                    self.update({
                        'move_line_nosuggest_ids': move_lines_commands
                    })
                    self._onchange_move_line_ids()
                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_SUCCESS +
                                    'Product: %s Qty: %s Lot: %s') % (
                                        self.product_id.display_name,
                                        1, barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_info',
                            {
                                'title': _("Succeed"),
                                'message': message,
                            })  



            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                # warning_mess = {
                #     'title': _('Alert!'),
                #     'message': 'Becareful! Quantity exceed than initial demand!'
                # }
                # return {'warning': warning_mess}

                if self.env.company.sudo(
                ).sh_stock_bm_is_notify_on_fail:
                    message = _(
                        CODE_SOUND_FAIL +
                        'Becareful! Quantity exceed than initial demand!'
                    )
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'sh_inventory_barcode_mobile_notification_danger',
                        {
                            'title': _("Failed"),
                            'message': message,
                        })
                return

                

        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    # raise UserError(
                    #     _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(CODE_SOUND_FAIL + "There are no available qty for this lot/serial.%s") % (barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return
                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, CODE_SOUND_FAIL)
                # Assign lot_id in move_lines_command
                if not lot:
                    # raise UserError(
                    #     _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. %s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(CODE_SOUND_FAIL + "Can't create Lots/Serial Number record for this lot/serial. %s") % (barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)

                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s Lot: %s') % (
                                                self.product_id.display_name,
                                                qty_done, barcode)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })  

                            break
                    else:
                        # move_lines_commands = self._generate_serial_move_line_commands(
                        #     [barcode])
                        move_lines_commands = []
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['qty_done'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        # move_lines_commands.append((0, 0, move_line_vals))
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': lot.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': self.location_id.id,
                        }

                        self.update({
                            'move_line_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, lot.name)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  
            # FOR SERIAL PRODUCT
            # --------------------------------------------
            # outgoing / internal - show_lots_m2o - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    # raise UserError(
                    #     _(warm_sound_code + "Serial Number already exist!"))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL +
                            'Serial Number already exist!'
                        )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)
                # First Time Scan
                # lines = self.move_line_ids.filtered(
                #     lambda r: r.lot_id.name == barcode)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, CODE_SOUND_FAIL)
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  



                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            message = _(CODE_SOUND_FAIL + 
                                'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            # res['warning'] = {'title': _(
                            #     'Warning'), 'message': message}
                            # return res
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                # message = _(
                                #     CODE_SOUND_FAIL +
                                #     'Serial Number already exist!'
                                # )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })
                            return

                        break
                else:
                    list_allocated_serial_ids = []
                    if self.move_line_ids:
                        for line in self.move_line_ids:
                            if line.lot_id:
                                list_allocated_serial_ids.append(
                                    line.lot_id.id)

                    # if need new line.
                    quant = quant_obj.search([
                        ('product_id', '=', self.product_id.id),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal'),
                        ('lot_id.name', '=', barcode),
                        ('location_id', 'child_of', self.location_id.id),
                        ('lot_id.id', 'not in', list_allocated_serial_ids),
                    ], limit=1)

                    # if not quant:
                    #     raise UserError(
                    #         _("There are no available qty for this lot/serial: %s") % (barcode))

                    if not quant and not self.picking_id.picking_type_id.use_create_lots:
                        # raise UserError(
                        #     _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            # message = _(
                            #     CODE_SOUND_FAIL +
                            #     'Scanned Internal Reference/Barcode not exist in any product!'
                            # )
                            message =  _(CODE_SOUND_FAIL + "There are no available qty for this lot/serial.%s") % (barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })
                        return

                    lot = False
                    if quant and quant.lot_id:
                        lot = quant.lot_id
                    else:
                        # Create New Lot if it's allow.
                        lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                            barcode, self.product_id.id, CODE_SOUND_FAIL)
                    # Assign lot_id in move_lines_command
                    if not lot:
                        # raise UserError(
                        #     _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. %s") % (barcode))

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            # message = _(
                            #     CODE_SOUND_FAIL +
                            #     'Scanned Internal Reference/Barcode not exist in any product!'
                            # )
                            message  = _(CODE_SOUND_FAIL + "Can't create Lots/Serial Number record for this lot/serial. %s") % (barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })
                        return

                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(
                        quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['qty_done'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    # New Barcode Scan then create new line
                    vals_line = {
                        'product_id': self.product_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'lot_id': lot.id,
                        'qty_done': 1,
                        'product_uom_id': self.product_uom.id,
                        'location_id': self.location_id.id,
                    }
                    self.update({
                        'move_line_ids':  move_lines_commands
                    })
                    self._onchange_move_line_ids()

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_SUCCESS +
                                    'Product: %s Qty: %s Lot: %s') % (
                                        self.product_id.display_name,
                                        1, lot.name)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_info',
                            {
                                'title': _("Succeed"),
                                'message': message,
                            })  

            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                # warning_mess = {
                #     'title': _('Alert!'),
                #     'message': 'Becareful! Quantity exceed than initial demand!'
                # }
                # return {'warning': warning_mess}
                if self.env.company.sudo(
                ).sh_stock_bm_is_notify_on_fail:
                    message = _(
                        CODE_SOUND_FAIL +
                        'Becareful! Quantity exceed than initial demand!'
                    )
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'sh_inventory_barcode_mobile_notification_danger',
                        {
                            'title': _("Failed"),
                            'message': message,
                        })
                return

        else:
            # raise UserError(
            #     _(warm_sound_code + "Picking type is not outgoing or incoming or internal transfer."))
            if self.env.company.sudo(
            ).sh_stock_bm_is_notify_on_fail:
                message = _(
                    CODE_SOUND_FAIL +
                    'Picking type is not outgoing or incoming or internal transfer.'
                )
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger',
                    {
                        'title': _("Failed"),
                        'message': message,
                    })
            return


    def sh_stock_move_barcode_mobile_has_tracking_show_lots_text(self, barcode, CODE_SOUND_SUCCESS, CODE_SOUND_FAIL):
        # self.picking_id.show_lots_text
        if self.picking_code == 'incoming':

            # FOR PURCHASE
            # LOT PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })
                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_nosuggest_ids.filtered(
                        lambda r: r.lot_name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s Lot: %s') % (
                                                self.product_id.display_name,
                                                qty_done, barcode)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })     

                            break

                    else:
                        move_lines_commands = self._generate_serial_move_line_commands(
                            [barcode])
                        # New Barcode Scan then create new line
                        # vals_line = {
                        #     'product_id': self.product_id.id,
                        #     'location_dest_id': self.location_dest_id.id,
                        #     'lot_name': barcode,
                        #     'qty_done': 1,
                        #     'product_uom_id': self.product_uom.id,
                        #     'location_id': self.location_id.id,
                        # }
                        self.update({
                            'move_line_nosuggest_ids': move_lines_commands
                        })

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

            # SERIAL PRODUCT
            # --------------------------------------------
            # incoming - show_lots_text - serial
            # --------------------------------------------
            if self.product_id.tracking == 'serial':
                # lot_names = self.env['stock.production.lot'].generate_lot_names(
                #     barcode, False)

                # VALIDATION SERIAL NO. ALREADY EXIST.
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == barcode)
                if lines:
                    # raise UserError(
                    #     _(warm_sound_code + "Serial Number already exist!"))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL +
                            'Serial Number already exist!'
                        )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                # First Time Scan
                lines = self.move_line_nosuggest_ids.filtered(
                    lambda r: r.lot_name == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode
                        }
                        self.update({
                            'move_line_nosuggest_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

                        break                        

                else:
                    move_lines_commands = self._generate_serial_move_line_commands(
                        [barcode])

                    # Create new line if not found any unallocated serial number line
                    # vals_line = {
                    #     'product_id': self.product_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'lot_name': barcode,
                    #     'qty_done': 1,
                    #     'product_uom_id': self.product_uom.id,
                    #     'location_id': self.location_id.id,
                    # }
                    self.update({
                        'move_line_nosuggest_ids': move_lines_commands
                    })

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_SUCCESS +
                                    'Product: %s Qty: %s Lot: %s') % (
                                        self.product_id.display_name,
                                        1, barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_info',
                            {
                                'title': _("Succeed"),
                                'message': message,
                            })  


            quantity_done = 0
            for move_line in self.move_line_nosuggest_ids:
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if quantity_done == self.product_uom_qty + 1:
                # warning_mess = {
                #     'title': _('Alert!'),
                #     'message': 'Becareful! Quantity exceed than initial demand!'
                # }
                # return {'warning': warning_mess}

                if self.env.company.sudo(
                ).sh_stock_bm_is_notify_on_fail:
                    message = _(
                        CODE_SOUND_FAIL +
                        'Becareful! Quantity exceed than initial demand!'
                    )
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'sh_inventory_barcode_mobile_notification_danger',
                        {
                            'title': _("Failed"),
                            'message': message,
                        })
                return


        elif self and self.picking_code in ['outgoing', 'internal']:
            # FOR SALE
            # LOT PRODUCT
            quant_obj = self.env['stock.quant']

            # FOR LOT PRODUCT
            # --------------------------------------------
            # outgoing / internal  - show_lots_text - lot
            # --------------------------------------------
            if self.product_id.tracking == 'lot':
                # First Time Scan
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id)
                ], limit=1)

                # if not quant:
                #     raise UserError(
                #         _("There are no available qty for this lot/serial.%s") % (barcode))

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    # raise UserError(
                    #     _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(CODE_SOUND_FAIL + "There are no available qty for this lot/serial.%s") % (barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, CODE_SOUND_FAIL)
                # Assign lot_id in move_lines_command
                if not lot:
                    # raise UserError(
                    #     _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(CODE_SOUND_FAIL + "Can't create Lots/Serial Number record for this lot/serial. %s") % (barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id == False)
                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = line.qty_done + 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_id': quant.lot_id.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, barcode)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

                        break
                else:
                    # Second Time Scan
                    lines = self.move_line_ids.filtered(
                        lambda r: r.lot_id.name == barcode)
                    if lines:
                        for line in lines:
                            # odoo v14 update below way
                            qty_done = line.qty_done + 1
                            vals_line = {
                                'qty_done': qty_done,
                            }
                            self.update({
                                'move_line_ids': [(1, line.id, vals_line)]
                            })
                            # odoo v14 update below way
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s Lot: %s') % (
                                                self.product_id.display_name,
                                                qty_done, barcode)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })  

                            break
                    else:
                        # move_lines_commands = self._generate_serial_move_line_commands(
                        #     [barcode])
                        move_lines_commands = []
                        lot = quant.lot_id
                        move_line_vals = self._prepare_move_line_vals(
                            quantity=0)
                        move_line_vals['lot_id'] = lot.id
                        move_line_vals['lot_name'] = lot.name
                        move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                        move_line_vals['qty_done'] = 1
                        move_lines_commands.append((0, 0, move_line_vals))

                        # move_lines_commands.append((0, 0, move_line_vals))
                        # New Barcode Scan then create new line
                        vals_line = {
                            'product_id': self.product_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'lot_id': quant.lot_id.id,
                            'qty_done': 1,
                            'product_uom_id': self.product_uom.id,
                            'location_id': quant.location_id.id,
                        }

                        self.update({
                            'move_line_ids': move_lines_commands
                        })
                        self._onchange_move_line_ids()

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            1, lot.name)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

            # FOR SERIAL PRODUCT
            # ----------------------------------------------
            # outgoing / internal  - show_lots_text - serial
            # ----------------------------------------------
            if self.product_id.tracking == 'serial':
                list_allocated_serial_ids = []
                if self.move_line_ids:
                    for line in self.move_line_ids:
                        if line.lot_id:
                            list_allocated_serial_ids.append(
                                line.lot_id.id)

                # if need new line.
                quant = quant_obj.search([
                    ('product_id', '=', self.product_id.id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('lot_id.name', '=', barcode),
                    ('location_id', 'child_of', self.location_id.id),
                    ('lot_id.id', 'not in', list_allocated_serial_ids),
                ], limit=1)

                # if not quant:
                #     raise UserError(
                #         _("There are no available qty for this lot/serial.%s") % (barcode))

                if not quant and not self.picking_id.picking_type_id.use_create_lots:
                    # raise UserError(
                    #     _(warm_sound_code + "There are no available qty for this lot/serial.%s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message =  _(CODE_SOUND_FAIL + "There are no available qty for this lot/serial.%s") % (barcode)
                        # message = _(
                        #     CODE_SOUND_FAIL +
                        #     'Serial Number already exist!'
                        # )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                lot = False
                if quant and quant.lot_id:
                    lot = quant.lot_id
                else:
                    # Create New Lot if it's allow.
                    lot = self.sh_stock_move_barcode_mobile_search_or_create_lot_serial_number(
                        barcode, self.product_id.id, CODE_SOUND_FAIL)
                # Assign lot_id in move_lines_command
                if not lot:
                    # raise UserError(
                    #     _(warm_sound_code + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_FAIL + "Can't create Lots/Serial Number record for this lot/serial. % s") % (barcode)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: r.lot_id.name == barcode)
                if lines:
                    # raise UserError(
                    #     _(warm_sound_code + "Serial Number already exist!"))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL +
                            'Serial Number already exist!'
                        )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return

                # First Time Scan
                lines = self.move_line_ids.filtered(
                    lambda r: not r.lot_id)

                if lines:
                    for line in lines:
                        # odoo v14 update below way
                        qty_done = 1
                        vals_line = {
                            'qty_done': qty_done,
                            'lot_name': barcode,
                            'lot_id': lot.id
                        }
                        self.update({
                            'move_line_ids': [(1, line.id, vals_line)]
                        })
                        # odoo v14 update below way
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_success:
                            message = _(CODE_SOUND_SUCCESS +
                                        'Product: %s Qty: %s Lot: %s') % (
                                            self.product_id.display_name,
                                            qty_done, lot.name)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })  

                        res = {}
                        if float_compare(line.qty_done, 1.0, precision_rounding=line.product_id.uom_id.rounding) != 0:
                            # message = _(
                            #     'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                            # res['warning'] = {'title': _(
                            #     'Warning'), 'message': message}
                            # return res
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(CODE_SOUND_FAIL + 
                                    'You can only process 1.0 %s of products with unique serial number.') % line.product_id.uom_id.name
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })
                            return

                        break
                else:
                    # list_allocated_serial_ids = []
                    # if self.move_line_ids:
                    #     for line in self.move_line_ids:
                    #         if line.lot_id:
                    #             list_allocated_serial_ids.append(
                    #                 line.lot_id.id)

                    # # if need new line.
                    # quant = quant_obj.search([
                    #     ('product_id', '=', self.product_id.id),
                    #     ('quantity', '>', 0),
                    #     ('location_id.usage', '=', 'internal'),
                    #     ('lot_id.name', '=', barcode),
                    #     ('location_id', 'child_of', self.location_id.id),
                    #     ('lot_id.id', 'not in', list_allocated_serial_ids),
                    # ], limit=1)

                    # if not quant:
                    #     raise UserError(
                    #         _("There are no available qty for this lot/serial: %s") % (barcode))

                    move_lines_commands = []
                    move_line_vals = self._prepare_move_line_vals(
                        quantity=0)
                    move_line_vals['lot_id'] = lot.id
                    move_line_vals['lot_name'] = lot.name
                    move_line_vals['product_uom_id'] = self.product_id.uom_id.id
                    move_line_vals['qty_done'] = 1
                    move_lines_commands.append((0, 0, move_line_vals))
                    # New Barcode Scan then create new line
                    # vals_line = {
                    #     'product_id': self.product_id.id,
                    #     'location_dest_id': self.location_dest_id.id,
                    #     'lot_id': quant.lot_id.id,
                    #     'qty_done': 1,
                    #     'product_uom_id': self.product_uom.id,
                    #     'location_id': quant.location_id.id,
                    # }
                    self.update({
                        'move_line_ids':  move_lines_commands
                    })
                    self._onchange_move_line_ids()
                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_SUCCESS +
                                    'Product: %s Qty: %s Lot: %s') % (
                                        self.product_id.display_name,
                                        1,  lot.name)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_info',
                            {
                                'title': _("Succeed"),
                                'message': message,
                            })  



            quantity_done = 0
            for move_line in self._get_move_lines():
                quantity_done += move_line.product_uom_id._compute_quantity(
                    move_line.qty_done, self.product_uom, round=False)

            if self.picking_code == 'outgoing' and quantity_done == self.product_uom_qty + 1:
                # warning_mess = {
                #     'title': _('Alert!'),
                #     'message': 'Becareful! Quantity exceed than initial demand!'
                # }
                # return {'warning': warning_mess}

                if self.env.company.sudo(
                ).sh_stock_bm_is_notify_on_fail:
                    message = _(
                        CODE_SOUND_FAIL +
                        'Becareful! Quantity exceed than initial demand!'
                    )
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'sh_inventory_barcode_mobile_notification_danger',
                        {
                            'title': _("Failed"),
                            'message': message,
                        })
                return

        else:
            # raise UserError(
            #     _(warm_sound_code + "Picking type is not outgoing or incoming or internal transfer."))

            if self.env.company.sudo(
            ).sh_stock_bm_is_notify_on_fail:
                message = _(
                    CODE_SOUND_FAIL +
                    'Picking type is not outgoing or incoming or internal transfer.'
                )
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger',
                    {
                        'title': _("Failed"),
                        'message': message,
                    })
            return

    # def sh_auto_serial_scanner_no_tracking(self, barcode, sequence, is_last_scanned, warm_sound_code):
    #     move_lines = False

    #     # INCOMING
    #     # ===================================
    #     if self.picking_code in ['incoming']:
    #         move_lines = self.move_line_nosuggest_ids

    #     # OUTGOING AND TRANSFER
    #     # ===================================
    #     elif self.picking_code in ['outgoing', 'internal']:
    #         move_lines = self.move_line_ids

    #     if move_lines:
    #         for line in move_lines:
    #             if self.product_id.barcode == barcode:
    #                 # odoo v14 update below way
    #                 qty_done = line.qty_done + 1
    #                 if self.picking_code in ['incoming']:
    #                     self.update({
    #                         'move_line_nosuggest_ids': [(1, line.id, {'qty_done': qty_done})]
    #                     })
    #                 if self.picking_code in ['outgoing', 'internal']:
    #                     self.update({
    #                         'move_line_ids': [(1, line.id, {'qty_done': qty_done})]
    #                     })
    #                 # odoo v14 update below way
    #                 if self.quantity_done == self.product_uom_qty + 1:
    #                     warning_mess = {
    #                         'title': _('Alert!'),
    #                         'message': 'Becareful! Quantity exceed than initial demand!'
    #                     }
    #                     return {'warning': warning_mess}
    #                 break
    #             else:
    #                 raise UserError(
    #                     _(warm_sound_code + "Scanned Internal Reference/Barcode not exist in any product"))
    #     else:
    #         raise UserError(
    #             _(warm_sound_code + "Pls add all product items in line than rescan."))

        # -----------------------------
        # sh_auto_serial_scanner
        # -----------------------------

        # =============================
        # UPDATED CODE
        # 15.0.23
        # move_lines = False

        # # INCOMING
        # # ===================================
        # if self.picking_code in ["incoming"]:
        #     move_lines = self.move_line_nosuggest_ids
        #
        # # OUTGOING AND TRANSFER
        # # ===================================
        # elif self.picking_code in ["outgoing", "internal"]:
        #     move_lines = self.move_line_ids
