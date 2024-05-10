# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import api, fields, models


class SalesOrderCount(models.Model):
    _inherit = 'sale.order'

    product_count = fields.Integer(string="Total QTY (Units)", compute='_compute_order_line_product_count')
    customer_type = fields.Selection([('person', 'Individual'),
                                      ('company', 'Company')], "Customer Type", related='partner_id.company_type',
                                     store=True)
    total_cost = fields.Monetary(currency_field='currency_id', string="Total Cost",
                                 compute='_compute_order_line_product_count')
    total_ref_amount = fields.Monetary(currency_field='currency_id', string="Total Amount",
                                       compute='_compute_order_line_product_count')

    def _compute_order_line_product_count(self):
        for res in self:
            count = 0
            cost = 0
            amount = 0
            for line in res.order_line:
                if line.product_id and line.product_id.name.startswith('REF.'):
                    count += line.product_uom_qty
                    cost += line.product_id.standard_price * line.product_uom_qty
                    amount += line.price_subtotal
            res.product_count = count
            res.total_cost = cost
            res.total_ref_amount = amount

class InvoiceOrderCount(models.Model):
    _inherit = 'account.move'

    product_count = fields.Integer(string="Total QTY (Units)", compute='_compute_order_line_product_count')

    def _compute_order_line_product_count(self):
        count = 0
        for res in self:
            for invoice_line in res.invoice_line_ids:
                count += invoice_line.quantity
            res.product_count = count
