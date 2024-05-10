# -*- encoding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import models, fields, api, _, tools

class SaleOrder(models.Model):
    _inherit = ["sale.order"]



    def get_product_weight(self):
        weightt = 0
        for line in self.order_line:
            weightt += line.product_id.weight
        return weightt


    def get_total_tax(self):
        account_move = self.env['account.move']

        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            res = order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)
            return res

        order = self
        tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                     compute_taxes)
        tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                  order.amount_untaxed, order.currency_id)

        fnl_total_tax = 0
        if tax_totals['groups_by_subtotal'] and 'Untaxed Amount' in tax_totals['groups_by_subtotal']:
            if tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0] and tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount'):
                fnl_total_tax = tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount')

        return round(fnl_total_tax, 2)

    def get_price_subtotal(self):
        total = 0
        for line in self.order_line:
            total += line.price_subtotal
        return round(total, 2)

    def get_line_discount(self):
        total = 0
        for line in self.order_line:
            total += line.discount
        return round(total, 2)


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def get_product_weight(self):
        weightt = 0
        for line in self.invoice_line_ids:
            weightt += line.product_id.weight
        return weightt

    def get_total_tax(self):
        account_move = self.env['account.move']

        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = self.invoice_line_ids
            res = order_line.tax_ids._origin.compute_all(price, order.currency_id, order_line.quantity,
                                                         product=order_line.product_id,
                                                         partner=order.partner_id)
            print("ssssssssssssssssssss", price)
            print("ssssssssssssssssssss", order)
            return res

        order = self
        tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.invoice_line_ids,
                                                                                     compute_taxes)
        tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                  order.amount_untaxed, order.currency_id)

        fnl_total_tax = 0
        if tax_totals['groups_by_subtotal'] and 'Untaxed Amount' in tax_totals['groups_by_subtotal']:
            if tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0] and tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount'):
                fnl_total_tax = tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount')

        return round(fnl_total_tax, 2)

    # def get_total_tax(self):
    #     account_move = self.env['account.move']
    #
    #     def compute_taxes(invoice_line_ids):
    #         price = invoice_line_ids.price_unit * (1 - (invoice_line_ids.discount or 0.0) / 100.0)
    #         order = self.id#invoice_line_ids.order_id
    #         res = invoice_line_ids.tax_id._origin.compute_all(price, order.currency_id, invoice_line_ids.product_uom_qty,
    #                                                      product=invoice_line_ids.product_id,
    #                                                      partner=order.partner_shipping_id)
    #         return res
    #
    #     order = self
    #     tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.invoice_line_ids,
    #                                                                                  compute_taxes)
    #     tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
    #                                               order.amount_untaxed, order.currency_id)
    #
    #     fnl_total_tax = 0
    #     if tax_totals['groups_by_subtotal'] and 'Untaxed Amount' in tax_totals['groups_by_subtotal']:
    #         if tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0] and tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount'):
    #             fnl_total_tax = tax_totals['groups_by_subtotal'].get('Untaxed Amount')[0].get('tax_group_amount')
    #
    #     return round(fnl_total_tax, 2)



    def get_price_subtotal(self):
        total = 0
        for line in self.invoice_line_ids:
            total += line.price_subtotal
        return round(total, 2)

    def get_line_discount(self):
        total = 0
        for line in self.invoice_line_ids:
            total += line.discount
        return round(total, 2)





