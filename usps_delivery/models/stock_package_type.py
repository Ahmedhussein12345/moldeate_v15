from odoo import fields, models


class ProductPackaging(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(selection_add=[('usps_ts', 'USPS')])
    girth = fields.Integer('Girth')

