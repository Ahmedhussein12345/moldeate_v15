# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
from odoo import api, fields, models


class LmResCompanyInherit(models.Model):
    _inherit = 'res.company'

    default_wr = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse")
    default_fc = fields.Many2one(comodel_name="account.fiscal.position", string="Fiscal Position")
    is_wr_so = fields.Boolean(string="Is Default Warehouse in Sales")
    is_fc_so = fields.Boolean(string="Is Default Fiscal Position in Sales")
