# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import api, fields, models


class LMAccJr(models.Model):
    _inherit = 'account.journal'

    is_moldeate_seq = fields.Boolean(string="For Moldeate Invoice")

    @api.onchange('type')
    def onchange_moldeate_seq_condition(self):
        value = [False for rec in self if rec.type != 'sale']
        if value:
            self.is_moldeate_seq = value[0]
        else:
            self.is_moldeate_seq = True


class LMAccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        rec = super(LMAccountMove, self).action_post()
        if self.journal_id.is_moldeate_seq:
            if self.move_type == 'out_invoice':
                if '/' in self.name:
                    name_split = self.name.split('/')
                    inv_number = name_split[-1][-5:]
                else:
                    inv_number = self.name[-5:]
                if self.invoice_origin:
                    sale_order = self.env['sale.order'].sudo().search([('name', '=', self.invoice_origin)])
                    if sale_order:
                        new_seq_with_so = sale_order.name + '/INV' + inv_number
                        self.name = new_seq_with_so
                    else:
                        self.name = 'INV' + inv_number
                else:
                    if self.name:
                        self.name = 'INV' + inv_number
        return rec

    # def action_post(self):
    #     rec = super(LMAccountMove, self).action_post()
    #     print ("Name ---------------", self.name)
    #     if self.journal_id.is_moldeate_seq:
    #         name_split = self.name.split('/')
    #         # new_seq_order = name_split[-3] + '/' + name_split[-2] + '/' + name_split[-1]
    #         new_seq_order = name_split[-2] + name_split[-1]
    #         # new_seq_order = "INV/00054"
    #         if self.move_type == 'out_invoice':
    #             if self.invoice_origin:
    #                 sales_obj = self.env['sale.order'].sudo().search([('name', '=', self.invoice_origin)])
    #                 new_seq_with_so = sales_obj.name + '/' + new_seq_order
    #                 self.update({'name': new_seq_with_so})
    #             else:
    #                 if self.name:
    #                     self.update({'name': new_seq_order})
    #         else:
    #             if self.name:
    #                 self.update({'name': new_seq_order})
    #     return rec
