from odoo import fields, models, api

class StockPackageType(models.Model):
    _inherit = 'stock.package.type'
    package_carrier_type = fields.Selection(
        selection_add=[('fedex_shipping_provider', 'Fedex'), ("stamps", "Stamps.com"), ('dhl_express', 'DHL Express'),
                       ("gls", "GLS"), ('ups_shipping_provider', 'UPS')])

