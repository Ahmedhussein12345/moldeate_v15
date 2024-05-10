import json
import requests
import base64
from odoo import tools
from odoo import models, fields, api
from requests.auth import HTTPBasicAuth
from odoo.modules.module import get_module_resource
from odoo.exceptions import UserError


class ShippingPartner(models.Model):
    _inherit = "shipping.partner"

    provider_company = fields.Selection(selection_add=[('ups_ts', 'UPS')])
    ups_user_name = fields.Char("User Name", copy=False)
    ups_password = fields.Char(string='Password', copy=False)
    ups_shipper_number = fields.Char(string='Shipper Number', copy=False)
    ups_access_lic_number = fields.Char(string='Access License Number', copy=False)

    @api.model
    def _ups_send_request(self, request_url, request_data, prod_environment, method='GET'):
        headers = {
            'Content-Type': 'application/json',
            'AccessLicenseNumber': self.ups_access_lic_number,
            'Username': self.ups_user_name,
            'Password': self.ups_password,
        }
        data = json.dumps(request_data)
        if prod_environment:
            api_url = 'https://onlinetools.ups.com/ship/v1' + request_url
        else:
            api_url = 'https://wwwcie.ups.com/ship/v1' + request_url
        try:
            req = requests.request(method, api_url, auth=HTTPBasicAuth(self.ups_user_name, self.ups_password),
                                   headers=headers,
                                   data=data)
            req.raise_for_status()
            if isinstance(req.content, bytes):
                req = req.content.decode("utf-8")
                response = json.loads(req)
            else:
                response = json.loads(req.content)
        except requests.HTTPError as e:
            raise UserError("%s" % req.text)
        return response

    @api.onchange('provider_company')
    def _onchange_provider_company(self):
        res = super(ShippingPartner, self)._onchange_provider_company()
        if self.provider_company == 'ups_ts' and not self.image:
            image_path = get_module_resource('ups_delivery', 'static/description', 'icon.png')
            self.image = base64.b64encode(open(image_path, 'rb').read())
        return res
