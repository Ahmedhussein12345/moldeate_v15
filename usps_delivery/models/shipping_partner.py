import base64
import requests
from odoo import models, fields, api
from odoo.modules.module import get_module_resource
from odoo.exceptions import Warning
from ..lib import xmltodict
# import xmltodict


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('usps_ts', 'USPS')])
    usps_user_id = fields.Char("USPS User ID", copy=False)

    _sql_constraints = [
        ('usps_user_id_uniq', 'unique (usps_user_id)', 'USPS user ID must be unique per Shipping Provider!'),
    ]

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'usps_ts':
            image_path = get_module_resource('usps_delivery', 'static/description', 'icon.png')
            self.image = base64.b64encode(open(image_path, 'rb').read())
        return res

    @api.model
    def _usps_send_request(self, params={}, prod_environment=True, method='GET'):
        log_obj = self.env['shipping.api.log']
        api_url = 'https://secure.shippingapis.com/ShippingAPI.dll' if prod_environment else 'https://stg-secure.shippingapis.com/ShippingAPI.dll'
        try:
            req = requests.request(method, api_url, params=params)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                response = req.content.decode("utf-8")
            else:
                response = req
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        log_obj.sudo().create({'shipping_partner_id': self.id, 'user_id': self.env.user.id, 'request_data': params, 'response_data': response})
        self._cr.commit()
        return xmltodict.parse(response)
