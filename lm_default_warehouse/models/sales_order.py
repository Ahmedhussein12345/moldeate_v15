# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, html_keep_url, is_html_empty


class LmSalesOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            if self.env.company.allow_warehouse:
                if not self.env.user.property_warehouse_id:
                    if self.company_id.is_wr_so and self.company_id.default_wr:
                        self.warehouse_id = self.company_id.default_wr.id
                    else:
                        warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
                        self.warehouse_id = warehouse_id or self.user_id.with_company(
                            self.company_id.id)._get_default_warehouse_id().id
            else:
                if self.company_id.is_wr_so and self.company_id.default_wr:
                    self.warehouse_id = self.company_id.default_wr.id
                else:
                    warehouse_id = self.env['ir.default'].get_model_defaults('sale.order').get('warehouse_id')
                    self.warehouse_id = warehouse_id or self.user_id.with_company(
                        self.company_id.id)._get_default_warehouse_id().id

    @api.onchange('partner_shipping_id', 'partner_id', 'company_id', 'warehouse_id')
    def onchange_partner_shipping_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        if self.company_id:
            if self.warehouse_id.default_fc:
                self.fiscal_position_id = self.warehouse_id.default_fc.id
            elif not self.warehouse_id.default_fc:
                if self.company_id.is_fc_so and self.company_id.default_fc:
                    self.fiscal_position_id = self.company_id.default_fc.id
                else:
                    self.fiscal_position_id = self.env['account.fiscal.position'].with_company(
                        self.company_id).get_fiscal_position(
                        self.partner_id.id, self.partner_shipping_id.id)
                    return {}

    @api.onchange('partner_id', 'warehouse_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if self.warehouse_id.default_fc:
            self.fiscal_position_id = self.warehouse_id.default_fc.id
        elif not self.warehouse_id.default_fc:
            if self.company_id.is_fc_so and self.company_id.default_fc:
                self.fiscal_position_id = self.company_id.default_fc.id
            else:
                if not self.partner_id:
                    self.update({
                        'partner_invoice_id': False,
                        'partner_shipping_id': False,
                        'fiscal_position_id': False,
                    })
                    return

                self = self.with_company(self.company_id)

                addr = self.partner_id.address_get(['delivery', 'invoice'])
                partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
                values = {
                    'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
                    'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
                    'partner_invoice_id': addr['invoice'],
                    'partner_shipping_id': addr['delivery'],
                }
                user_id = partner_user.id
                if not self.env.context.get('not_self_saleperson'):
                    user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
                if user_id and self.user_id.id != user_id:
                    values['user_id'] = user_id

                if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
                    if self.terms_type == 'html' and self.env.company.invoice_terms_html:
                        baseurl = html_keep_url(self.get_base_url() + '/terms')
                        values['note'] = _('Terms & Conditions: %s', baseurl)
                    elif not is_html_empty(self.env.company.invoice_terms):
                        values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
                if not self.env.context.get('not_self_saleperson') or not self.team_id:
                    default_team = self.env.context.get('default_team_id', False) or self.partner_id.team_id.id
                    values['team_id'] = self.env['crm.team'].with_context(
                        default_team_id=default_team
                    )._get_default_team_id(
                        domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)],
                        user_id=user_id)
                self.update(values)


class LmStockWarehouseInherit(models.Model):
    _inherit = 'stock.warehouse'

    default_fc = fields.Many2one(comodel_name="account.fiscal.position", string="Fiscal Position")
