from odoo.exceptions import Warning,ValidationError, UserError
from odoo import models, fields, api, _
import requests
import base64
import xml.etree.ElementTree as etree
from odoo.addons.vrajacombo_shipping_integration.models.vraja_combo_response import Response
from odoo.addons.vrajacombo_shipping_integration.fedex.base_service import FedexError, FedexFailure
from odoo.addons.vrajacombo_shipping_integration.fedex.tools.conversion import basic_sobject_to_dict
from odoo.addons.vrajacombo_shipping_integration.fedex.services.rate_service import FedexRateServiceRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.ship_service import FedexDeleteShipmentRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.ship_service import FedexProcessShipmentRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.address_validation_service import FedexAddressValidationRequest
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #fedex code
    fedex_third_party_account_number_sale_order = fields.Char(copy=False, string='FexEx Third-Party Account Number',
                                                              help="Please Enter the Third Party account number ")
    fedex_bill_by_third_party_sale_order = fields.Boolean(string="FedEx Third Party Payment", copy=False, default=False,
                                                          help="when this fields is true,then we can visible fedex_third party account number")

    #stamps code
    stamp_shipping_charge_ids = fields.One2many("stamp.shipping.charge", "sale_order_id", string="Stamp Rate Matrix")
    stamp_shipping_charge_id = fields.Many2one("stamp.shipping.charge", string="Stamp Service",
                                               help="This Method Is Use Full For Generating The Label", copy=False)

    #GLS Code
    gls_location_ids = fields.One2many("gls.locations", "sale_order_id",
                                       string="Gls ParcelShop Locations")
    gls_location_id = fields.Many2one("gls.locations", string="Gls ParcelShop Locations",
                                      help="Gls ParcelShop Locations locations", copy=False)

    #ups code
    ups_shipping_location_ids = fields.One2many("ups.location", "ups_sale_order_id",
                                                string="UPS Locations")
    ups_shipping_location_id = fields.Many2one("ups.location", string="UPS Locations",
                                               help="UPS Locations", copy=False)
    ups_service_rate = fields.Float(string="UPS Rate", copy=False)

    @api.depends('order_line')
    def _compute_bulk_weight(self):
        weight = 0.0
        for line in self.order_line:
                weight += line.product_uom_id._compute_quantity(line.product_uom_qty, line.product_id.uom_id) * line.product_id.weight
        self.weight_bulk = weight
    
    
    def manage_fedex_packages(self, rate_request, package_data, number=1,total_weight=0.0):
        package_weight = rate_request.create_wsdl_object_of_type('Weight')
        package_weight.Value = total_weight
        package_weight.Units = self.carrier_id.fedex_weight_uom
        package = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package.Weight = package_weight
        if self.carrier_id.fedex_default_product_packaging_id.shipper_package_code == 'YOUR_PACKAGING':
            package.Dimensions.Length = package_data and package_data.length
            package.Dimensions.Width = package_data and package_data.width
            package.Dimensions.Height =  package_data and package_data.height
            package.Dimensions.Units = 'IN' if self.carrier_id.fedex_weight_uom == 'LB' else 'CM'
        package.PhysicalPackaging = 'BOX'
        package.GroupPackageCount = 1
        if number:
            package.SequenceNumber = number
        return package

    # def fedex_shipping_provider_get_shipping_charges(self):
    #     res=self.get_fedex_rate()
    #     self.set_delivery_line()
    #     return res


    # def get_fedex_rate(self):
    #     self.ensure_one()
    #     immediate_payment_term_id = self.env.ref('account.account_payment_term_immediate').id
    #     if self.carrier_id.delivery_type=='fedex_shipping_provider':
    #         shipping_charge = 0.0
    #         weight = 0.0
    #         for line in self.order_line:
    #             weight += line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id) * line.product_id.weight
    #
    #         _logger.info('Product Weight : %s ' % (weight))
    #         # Shipper and Recipient Address
    #         shipper_address = self.warehouse_id.partner_id
    #         recipient_address = self.partner_id
    #         shipping_credential = self.carrier_id.company_id
    #
    #         # check sender Address
    #         if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
    #             raise Warning(_("Please Define Proper Sender Address!"))
    #
    #         # check Receiver Address
    #         if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
    #             raise Warning(_("Please Define Proper Recipient Address!"))
    #         try:
    #             # This is the object that will be handling our request.
    #             FedexConfig = shipping_credential.get_fedex_api_object(self.carrier_id.prod_environment)
    #             rate_request = FedexRateServiceRequest(FedexConfig)
    #             package_type = self.carrier_id.fedex_default_product_packaging_id.shipper_package_code
    #             rate_request = self.carrier_id.prepare_shipment_request(shipping_credential, rate_request, shipper_address,
    #                                                          recipient_address, package_type,self)
    #             rate_request.RequestedShipment.PreferredCurrency = self.company_id and self.company_id.currency_id and self.company_id.currency_id.name
    #
    #             _logger.info('Fedex Package Details : %s ' % (self.custom_package_ids))
    #             if not self.custom_package_ids:
    #
    #                 total_weight=self.company_id.weight_convertion(self.carrier_id and self.carrier_id.fedex_weight_uom,weight)
    #                 package = self.carrier_id.manage_fedex_packages(rate_request, total_weight)
    #                 rate_request.add_package(package)
    #
    #                 _logger.info('Total Weight : %s ' % (total_weight))
    #                 _logger.info('Package : %s ' % (package))
    #
    #
    #             for sequence, package in enumerate(self.custom_package_ids, start=1):
    #                 total_weight = self.company_id.weight_convertion(
    #                     self.carrier_id and self.carrier_id.fedex_weight_uom, package.shipping_weight)
    #                 package = self.manage_fedex_packages(rate_request, package, sequence,total_weight)
    #                 rate_request.add_package(package)
    #
    #             if self.carrier_id.fedex_onerate:
    #                 rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['FEDEX_ONE_RATE']
    #             rate_request.send_request()
    #         except FedexError as ERROR:
    #             raise Warning(_("Request Data Is Not Correct! %s "%(ERROR.value)))
    #             # raise ValidationError(ERROR.value)
    #         except FedexFailure as ERROR:
    #             raise Warning(_("Request Data Is Not Correct! %s " % (ERROR.value)))
    #             # raise ValidationError(ERROR.value)
    #         except Exception as e:
    #             raise Warning(_("Request Data Is Not Correct! %s " % (e)))
    #             # raise ValidationError(e)
    #         for shipping_service in rate_request.response.RateReplyDetails:
    #             for rate_info in shipping_service.RatedShipmentDetails:
    #                 shipping_charge = float(rate_info.ShipmentRateDetail.TotalNetFedExCharge.Amount)
    #                 shipping_charge_currency = rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency
    #                 if self.company_id and self.company_id.currency_id and self.company_id.currency_id.name != rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency:
    #                     rate_currency = self.env['res.currency'].search([('name', '=', shipping_charge_currency)],
    #                                                                     limit=1)
    #                     if rate_currency:
    #                         shipping_charge = rate_currency.compute(float(shipping_charge), self.company_id and self.company_id.currency_id and self.company_id.currency_id)
    #         self.delivery_price=float(shipping_charge) + self.carrier_id.add_custom_margin
    #         self.delivery_rating_success = True
    #         if self.payment_term_id and self.payment_term_id.id == immediate_payment_term_id:
    #             self.set_delivery_line()
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': "Yeah! Shipping Charge has been retrieved.",
    #             'img_url': '/web/static/src/img/smile.svg',
    #             'type': 'rainbow_man',
    #         }
    #     }

    #Gls Method
    def get_locations(self):
        order = self
        # Shipper and Recipient Address
        shipper_address = order.warehouse_id.partner_id
        recipient_address = order.partner_shipping_id
        # check sender Address
        if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
            raise ValidationError("Please Define Proper Sender Address!")
        # check Receiver Address
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")
        if not self.carrier_id.company_id:
            raise ValidationError("Credential not available!")

        try:
            gls_location_request = etree.Element("Envelope")
            gls_location_request.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
            body_node = etree.SubElement(gls_location_request, "Body")
            parcel_shop_search_location = etree.SubElement(body_node, 'ParcelShopSearchLocation')
            parcel_shop_search_location.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/ParcelShop"
            etree.SubElement(parcel_shop_search_location, 'Street').text = str(recipient_address.street or "")
            etree.SubElement(parcel_shop_search_location, 'StreetNumber').text = str(recipient_address.street2 or "")
            etree.SubElement(parcel_shop_search_location, 'CountryCode').text = str(
                recipient_address.country_id.code or "")
            etree.SubElement(parcel_shop_search_location, 'Province').text = str(recipient_address.state_id.name or "")
            etree.SubElement(parcel_shop_search_location, 'ZIPCode').text = str(recipient_address.zip or "")
            etree.SubElement(parcel_shop_search_location, 'City').text = str(recipient_address.city or "")
            _logger.info("=====>Get Location Request Data %s" % etree.tostring(gls_location_request))
        except Exception as e:
            raise ValidationError(e)

        try:
            username = int(self.company_id.gls_user_id)
            password = self.company_id.gls_password
            data = "%s:%s" % (username, password)
            encode_data = base64.b64encode(data.encode("utf-8"))
            authorization_data = "Basic %s" % (encode_data.decode("utf-8"))
            headers = {
                'SOAPAction': 'http://fpcs.gls-group.eu/v1/getParcelShop',
                'Content-Type': 'text/xml; charset="utf-8"',
                'Authorization': authorization_data
            }
            url = "%s/backend/ParcelShopService/ParcelShopPortType" % (self.company_id.gls_api_url)
            response_data = requests.post(url=url, data=etree.tostring(gls_location_request), headers=headers)
            _logger.info("=====>Get Location Response%s" % response_data)
        except Exception as e:
            raise ValidationError(e)
        if response_data.status_code in [200, 201]:
            api = Response(response_data)
            response_data = api.dict()
            _logger.info("=====>Get Location Response JSON%s" % response_data)
            gls_locations = self.env['gls.locations']
            existing_records = self.env['gls.locations'].search(
                [('sale_order_id', '=', order and order.id)])
            existing_records.sudo().unlink()

            if response_data:
                if isinstance(response_data, dict):
                    response_data = [response_data]
                # locations = response_data[0].get('Envelope').get('Body').get('ListOfParcelShop').get('ParcelShop')
                locations = response_data[0] and response_data[0].get('Envelope') and response_data[0].get(
                    'Envelope').get('Body') and \
                            response_data[0].get('Envelope').get('Body').get('ListOfParcelShop') and \
                            response_data[0].get('Envelope').get('Body').get('ListOfParcelShop').get('ParcelShop')

                if locations == None:
                    raise ValidationError("%s" % (response_data))
                for location in locations:
                    point_relais_id = gls_locations.sudo().create(
                        {'gls_location_parcelshopid': location.get('ParcelShopID') or "",
                         'gls_location_name1': location.get('Address').get('Name1') or "",
                         # 'gls_location_name2': location.get('Address').get('Name2') or "",
                         'gls_location_countrycode': location.get('Address').get('CountryCode') or "",
                         'gls_location_zipcode': location.get('Address').get('ZIPCode') or "",
                         'gls_location_city': location.get('Address').get('City') or "",
                         'gls_location_street': location.get('Address').get('Street') or "",
                         'gls_location_streetnumber': location.get('Address').get('StreetNumber') or "",
                         'sale_order_id': self.id})
            else:
                raise ValidationError("Location Not Found For This Address! %s " % (response_data))
        else:
            raise ValidationError("%s %s" % (response_data, response_data.text))
    #ups methods
    def location_api_request_data(self):
        """ this method return request data of location api"""
        recipient_address = self.partner_shipping_id

        # check Receiver Address
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")
        if not self.carrier_id.company_id:
            raise ValidationError("Credential not available!")

        master_node_AccessRequest = etree.Element("AccessRequest")
        master_node_AccessRequest.attrib['xml:lang'] = "en-US"
        etree.SubElement(master_node_AccessRequest,'AccessLicenseNumber').text ="{}".format(self.company_id.access_license_number)
        etree.SubElement(master_node_AccessRequest, 'UserId').text = "{}".format(self.company_id.ups_userid)
        etree.SubElement(master_node_AccessRequest, 'Password').text = "{}".format(self.company_id.ups_password)
        master_node_LocatorRequest = etree.Element("LocatorRequest")
        sub_root_node_Request = etree.SubElement(master_node_LocatorRequest, 'Request')
        etree.SubElement(sub_root_node_Request, "RequestAction").text = "Locator"
        etree.SubElement(sub_root_node_Request, "RequestOption").text = "{}".format(self.carrier_id and self.carrier_id.ups_request_option)
        sub_root_node_OriginAddress = etree.SubElement(master_node_LocatorRequest, "OriginAddress")
        sub_root_node_AddressKeyFormat = etree.SubElement(sub_root_node_OriginAddress, 'AddressKeyFormat')
        etree.SubElement(sub_root_node_AddressKeyFormat, 'AddressLine').text = "{}".format(recipient_address.street)
        etree.SubElement(sub_root_node_AddressKeyFormat, 'PoliticalDivision2').text = "{}".format(recipient_address.city)
        etree.SubElement(sub_root_node_AddressKeyFormat, 'PoliticalDivision1').text = "{}".format(recipient_address.state_id.code)
        etree.SubElement(sub_root_node_AddressKeyFormat, 'PostcodePrimaryLow').text = "{}".format(recipient_address.zip)
        etree.SubElement(sub_root_node_AddressKeyFormat, 'CountryCode').text = "{}".format(
            recipient_address.country_id.code)
        sub_root_node_Translate = etree.SubElement(master_node_LocatorRequest, "Translate")
        etree.SubElement(sub_root_node_Translate, 'LanguageCode').text = "{}".format("ENG")
        sub_root_node_UnitOfMeasurement = etree.SubElement(master_node_LocatorRequest, "UnitOfMeasurement")
        etree.SubElement(sub_root_node_UnitOfMeasurement, 'Code').text = "{}".format(self.carrier_id and self.carrier_id.ups_measurement_code)
        sub_root_node_LocationSearchCriteria = etree.SubElement(master_node_LocatorRequest, 'LocationSearchCriteria')
        sub_root_node_ServiceSearch = etree.SubElement(sub_root_node_LocationSearchCriteria, "ServiceSearch")
        sub_root_node_ServiceCode = etree.SubElement(sub_root_node_ServiceSearch, 'ServiceCode')
        etree.SubElement(sub_root_node_ServiceCode, 'Code').text = "{}".format(self.carrier_id and self.carrier_id.ups_service_code)
        _reqString = etree.tostring(master_node_AccessRequest)

        tree = etree.ElementTree(etree.fromstring(_reqString))
        root = tree.getroot()

        _QuantunmRequest = etree.tostring(master_node_LocatorRequest)
        quantunmTree = etree.ElementTree(etree.fromstring(_QuantunmRequest))
        quantRoot = quantunmTree.getroot()
        _XmlRequest = etree.tostring(root, encoding='utf8', method='xml') + etree.tostring(quantRoot, encoding='utf8',
                                                                                     method='xml')
        _XmlRequest = _XmlRequest.decode().replace('\n', '')
        return _XmlRequest
    def ups_get_locations(self):
        """ this method return ups location"""
        if not self.carrier_id and self.carrier_id.prod_environment:
            api_url = 'https://wwwcie.ups.com/ups.app/xml/Locator'
        else:
            api_url = 'https://onlinetools.ups.com/ups.app/xml/Locator'
        request_data = self.location_api_request_data()
        try:
            response_data = requests.post(url=api_url,data=request_data)
            if response_data.status_code in [200,201]:
                _logger.info("Get Successfully Response From {}".format(api_url))
                response_data = Response(response_data)
                result = response_data.dict()
                drop_location =result.get('LocatorResponse').get('SearchResults').get('DropLocation')
                if not drop_location:
                    raise ValidationError("Drop Location Not Found {}".format(result))
                ups_locations = self.env['ups.location']
                existing_records = self.env['ups.location'].search(
                    [('ups_sale_order_id', '=', self.id)])
                existing_records.sudo().unlink()
                for location in drop_location:
                    location_id = location.get('LocationID')
                    location_street = location.get('AddressKeyFormat').get('AddressLine')
                    location_city = location.get('AddressKeyFormat').get('PoliticalDivision2')
                    location_area = location.get('AddressKeyFormat').get('PoliticalDivision3')
                    location_state = location.get('AddressKeyFormat').get('PoliticalDivision1')
                    location_zip = location.get('AddressKeyFormat').get('PostcodePrimaryLow')
                    location_country_code =location.get('AddressKeyFormat').get('CountryCode')
                    sale_order_id = self.id
                    ups_locations.sudo().create(
                        {
                            'location_id':"{}".format(location_id),
                            'street':'{}'.format(location_street),
                            'street2': '{}'.format(location_area),
                            'city': '{}'.format(location_city),
                            'state_code': '{}'.format(location_state),
                            'zip': '{}'.format(location_zip),
                            'country_code': '{}'.format(location_country_code),
                            'ups_sale_order_id': '{}'.format(sale_order_id),
                        }
                    )
            else:
                raise ValidationError(response_data.text)
        except Exception as E:
            raise ValidationError(E)
    
