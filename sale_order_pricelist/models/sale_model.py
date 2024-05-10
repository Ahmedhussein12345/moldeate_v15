# -*- encoding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import models, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange('partner_id')
    def get_pricelist(self):
        self.pricelist_id = self.partner_id.property_product_pricelist