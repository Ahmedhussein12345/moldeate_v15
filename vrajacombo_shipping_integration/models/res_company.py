from odoo import models, fields, api, _
import requests
from odoo.addons.vrajacombo_shipping_integration.fedex.config import FedexConfig
from odoo.addons.vrajacombo_shipping_integration.models.vraja_combo_response import Response
from odoo.addons.vrajacombo_shipping_integration.ups_api.ups_request import UPS_API

from odoo.exceptions import ValidationError
import xml.etree.ElementTree as etree

import logging
_logger = logging.getLogger("Vraja Combo")



class ResCompany(models.Model):
    _inherit = 'res.company'

    #fedex
    use_fedex_shipping_provider = fields.Boolean(copy=False, string="Are You Use FedEx Shipping Provider.?",
                                                 help="If use fedEx shipping provider than value set TRUE.",
                                                 default=False)
    use_address_validation_service = fields.Boolean(copy=False, string="Use Address Validation Service",
                                                    help="Use Address Validation service to identify residential area or not.\nTo use address validation services, client need to request fedex to enable this service for his account.By default, The service is disable and you will receive authentication failed.")
    fedex_key = fields.Char(string="Developer Key", help="Developer key", copy=False)
    fedex_password = fields.Char(copy=False, string='Password',
                                 help="The Fedex-generated password for your Web Systems account. This is generally emailed to you after registration.")
    fedex_account_number = fields.Char(copy=False, string='Account Number',
                                       help="The account number sent to you by Fedex after registering for Web Services.")
    fedex_meter_number = fields.Char(copy=False, string='Meter Number',
                                     help="The meter number sent to you by Fedex after registering for Web Services.")
    fedex_integration_id = fields.Char(copy=False, string='Integration ID',
                                       help="The integrator string sent to you by Fedex after registering for Web Services.")

    #USPS(Stamps.com)

    stamps_user_name = fields.Char(string="Stamps User Name", help="Provided By Stamps.com", copy=False)
    stamps_password = fields.Char(copy=False, string='Stamps Password', help="Provided By Stamps.com")
    stamps_integrator_id = fields.Char(string="IntegratorTxID", help="Provided By Stamps.com", copy=False)

    stamps_api_url = fields.Char(copy=False, string='Stamps API URL',
                                 help="API URL, Redirect to this URL when calling the API.",
                                 default="https://swsim.testing.stamps.com/swsim/swsimv90.asmx")
    use_stamps_shipping_provider = fields.Boolean(copy=False, string="Are You Using Stamps.com?",
                                                  help="If use stamps.com shipping Integration than value set TRUE.",
                                                  default=False)
    stamps_authenticator = fields.Text(string="Stamps.com Authenticator", help="Provided By Stamps.com", copy=False)

    #DHL EXPRESS
    dhl_express_userid = fields.Char("DHL Express UserId", copy=False, help="User ID")
    dhl_express_password = fields.Char("DHL Express Password", copy=False,
                                       help="The DHL generated password for your Web Systems account.")
    dhl_express_account_number = fields.Char("DHL Express Account No", copy=False,
                                             help="The account number sent to you by DHL.")
    use_dhl_express_shipping_provider = fields.Boolean(copy=False, string="Are You Using DHL Express?",
                                                       help="If you use DHL Express integration then set value to TRUE.",
                                                       default=False)

    #gls
    gls_user_id = fields.Char(string="GLS UserID", help="GLS User ID provided by GLS..", copy=False)
    gls_password = fields.Char(copy=False, string='GLS Password', help="GLS Password provided by GLS.")
    gls_contact_id = fields.Char(string="GLS Contact ID", help="GLS Contact ID provided by GLS..", copy=False)

    gls_api_url = fields.Char(copy=False, string='GLS API URL',
                              help="API URL, Redirect to this URL when calling the API.",
                              default="https://shipit-customer-test.gls-group.eu:8443")
    use_gls_shipping_provider = fields.Boolean(copy=False, string="Are You Using GLS?",
                                               help="If use GLS shipping Integration than value set TRUE.",
                                               default=False)
    gls_tracking_url = fields.Char(copy=False, string='GLS Tracking URL',
                                   help="API URL, Redirect to this URL when calling the Track Tool.",
                                   default="https://gls-group.eu/DE/de/paketverfolgung?match=")

    #ups
    use_ups_shipping_provider = fields.Boolean(copy=False, string="Are You Use UPS Shipping Provider.?",
                                               help="If use UPS shipping provider than value set TRUE.", default=False)

    access_license_number = fields.Char("AccessLicenseNumber")
    ups_userid = fields.Char("UPS UserId")
    ups_password = fields.Char("UPS Password")
    ups_shipper_number = fields.Char("UPS Shipper Number")
    check_recipient_address = fields.Boolean(copy=False, string="Check Recipient Address")
    mail_template_id = fields.Many2one('mail.template', 'E-mail Template')
    is_automatic_shipment_mail = fields.Boolean('Automatic Send Shipment Confirmation Mail')

    #fedex_method
    def get_fedex_api_object(self, prod_environment=False):
        return FedexConfig(key = self.fedex_key,
                password = self.fedex_password,
                account_number = self.fedex_account_number,
                meter_number = self.fedex_meter_number,
                integrator_id=self.fedex_integration_id,
                use_test_server = not prod_environment)

    # def weight_convertion(self, weight_unit, weight):
    #     pound_for_kg = 2.20462
    #     ounce_for_kg = 35.274
    #     if weight_unit in ["LB", "LBS"]:
    #         return round(weight * pound_for_kg, 3)
    #     elif weight_unit in ["OZ", "OZS"]:
    #         return round(weight * ounce_for_kg, 3)
    #     else:
    #         return round(weight, 3)

    #USPS (stamps.com)method
    def generate_stamps_authenticator(self):
        url = "%s" % (self.stamps_api_url)
        headers = {
            'SOAPAction': "http://stamps.com/xml/namespace/2019/09/swsim/SwsimV84/AuthenticateUser",
            'Content-Type': 'text/xml; charset="utf-8"'
        }
        master_node = etree.Element('Envelope')
        master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, 'Body')

        root_node = etree.SubElement(submater_node, "AuthenticateUser")
        root_node.attrib['xmlns'] = "http://stamps.com/xml/namespace/2019/09/swsim/SwsimV84"
        shipment_data = etree.SubElement(root_node, "Credentials")

        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (self.stamps_integrator_id)
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.stamps_password)
        request_data = etree.tostring(master_node)
        try:
            _logger.info("Stamps Authenticator Request Data : %s" % (request_data))
            result = requests.post(url=url, data=request_data, headers=headers)
        except Exception as e:
            raise ValidationError(e)
        if result.status_code != 200:
            raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
        api = Response(result)
        result = api.dict()
        if result.get('Envelope') and result.get('Envelope').get('Body') and result.get('Envelope').get('Body').get(
                'AuthenticateUserResponse') and result.get('Envelope').get('Body').get('AuthenticateUserResponse').get(
                'Authenticator'):
            self.stamps_authenticator = result.get('Envelope').get('Body').get('AuthenticateUserResponse').get(
                'Authenticator')
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': "Yeah! Shipping Charge has been retrieved.",
                    'img_url': '/web/static/src/img/smile.svg',
                    'type': 'rainbow_man',
                }
            }
        else:
            raise ValidationError("%s" % (result))

    #UPS
    def get_ups_api_object(self, environment, service_name, ups_user_id, ups_password, ups_access_license_number):
        api = UPS_API(environment, service_name, ups_user_id, ups_password, ups_access_license_number, timeout=500)
        return api

    def weight_convertion(self, weight_unit, weight):
        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        pound_for_kg = 2.20462
        ounce_for_lb = 16
        ounce_for_kg = 35.274
        if uom_id.name in ['lb', 'lbs', 'LB', 'LBS'] and weight_unit in ["LB", "LBS"]:
            return round(weight, 3)
        elif uom_id.name in ['kg', 'KG'] and weight_unit in ["LB", "LBS"]:
            return round(weight * pound_for_kg, 3)
        elif uom_id.name in ['lb', 'lbs', 'LB', 'LBS'] and weight_unit in ["OZ", "OZS"]:
            return round(weight * ounce_for_lb, 3)
        elif uom_id.name in ['kg', 'KG'] and weight_unit in ["OZ", "OZS"]:
            return round(weight * ounce_for_kg, 3)
        else:
            return round(weight, 3)

class UPSPackageDetails(models.Model):
    _inherit = "stock.quant.package"
    custom_ups_tracking_number = fields.Char(string="UPS Tracking Number",
                                             help="If tracking number available print it in this field.")


