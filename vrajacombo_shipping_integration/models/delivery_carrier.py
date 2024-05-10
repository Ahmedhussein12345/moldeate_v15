import binascii
from math import ceil
import time
import datetime
from datetime import datetime
from odoo.addons.vrajacombo_shipping_integration.dhl_api.dhl_request import DHL_API
from requests import request
import base64
import requests
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError
import xml.etree.ElementTree as etree
from odoo.addons.vrajacombo_shipping_integration.models.vraja_combo_response import Response
from odoo.addons.vrajacombo_shipping_integration.fedex.base_service import FedexError, FedexFailure
from odoo.addons.vrajacombo_shipping_integration.fedex.tools.conversion import basic_sobject_to_dict
from odoo.addons.vrajacombo_shipping_integration.fedex.services.rate_service import FedexRateServiceRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.ship_service import FedexDeleteShipmentRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.ship_service import FedexProcessShipmentRequest
from odoo.addons.vrajacombo_shipping_integration.fedex.services.address_validation_service import \
    FedexAddressValidationRequest
import logging
_logger = logging.getLogger("Vraja Combo")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(
        selection_add=[('fedex_shipping_provider', 'Fedex'), ("ups_shipping_provider", "UPS"), ("stamps", "Stamps.com"),
                       ("dhl_express", "DHL Express"), ("gls", "GLS")],
        ondelete={'fedex_shipping_provider': 'set default', "ups_shipping_provider": 'set default',
                  "stamps": 'set default', "dhl_express": 'set default', "gls": 'set default'})
    # fedex fields
    add_custom_margin = fields.Float(string="Margin", help="Add This Margin In Rate When Rate Comes From FedEx.",
                                     default=0.0)
    fedex_service_type = fields.Selection(
        [('EUROPE_FIRST_INTERNATIONAL_PRIORITY', 'Europe First International Priority'),
         ('SMART_POST', 'Smart Post'),  # When Call the service given the error "Customer not eligible for service"
         ('FEDEX_GROUND', 'Fedex Ground'),  # When Call the service given the error "Customer not eligible for service"
         ('FEDEX_DISTANCE_DEFERRED', 'Fedex Distance Deferred'),
         # for domestic UK pickup  Error : Customer is eligible.
         ('FEDEX_NEXT_DAY_AFTERNOON', 'Fedex Next Day Afternoon'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_EARLY_MORNING', 'Fedex Next Day Early Morning'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_END_OF_DAY', 'Fedex Next Day End of Day'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_FREIGHT', 'Fedex Next Day Freight'),  # for domestic UK pickup
         ('FEDEX_NEXT_DAY_MID_MORNING', 'Fedex Next Day Mid Morning'),  # for domestic UK pickup
         ('GROUND_HOME_DELIVERY', 'Ground Home Delivery'),
         # To Address Use: 33122 Florida Doral US. From Add use: 33122 Florida Doral US and Package type box is your_packaging.
         ('INTERNATIONAL_ECONOMY', 'International Economy'),
         # To Address Use: 33122 Florida Doral US. From Add use: 12277 Germany Berlin Penna.
         ('INTERNATIONAL_FIRST', 'International First'),
         # To Address Use: 33122 Florida Doral US. From Add use: 12277 Germany Berlin Penna.
         ('INTERNATIONAL_PRIORITY', 'International Priority'),
         # To Address Use: 33122 Florida Doral US. From Add use: 73377 "Le Bourget du Lac" France
         ('FIRST_OVERNIGHT', 'First Overnight'),  # for US
         ('PRIORITY_OVERNIGHT', 'Priority Overnight'),  # for US
         ('FEDEX_2_DAY', 'Fedex 2 Day'),  # for US Use: 33122 Florida Doral
         ('FEDEX_2_DAY_AM', 'Fedex 2 Day AM'),  # for US Use: 33122 Florida Doral
         ('FEDEX_EXPRESS_SAVER', 'Fedex Express Saver'),  # for US Use: 33122 Florida Doral
         ('STANDARD_OVERNIGHT', 'Standard Overnight')  # for US Use: 33122 Florida Doral
         ], string="Service Type", help="Shipping Services those are accepted by Fedex")

    fedex_droppoff_type = fields.Selection([('BUSINESS_SERVICE_CENTER', 'Business Service Center'),
                                            ('DROP_BOX', 'Drop Box'),
                                            ('REGULAR_PICKUP', 'Regular Pickup'),
                                            ('REQUEST_COURIER', 'Request Courier'),
                                            ('STATION', 'Station')],
                                           string="Drop-off Type",
                                           default='REGULAR_PICKUP',
                                           help="Identifies the method by which the package is to be tendered to FedEx.")
    fedex_default_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    fedex_weight_uom = fields.Selection([('LB', 'LB'),
                                         ('KG', 'KG')], default='LB', string="Weight UoM",
                                        help="Weight UoM of the Shipment")
    fedex_collection_type = fields.Selection([('ANY', 'ANY'),
                                              ('CASH', 'CASH'),
                                              ('COMPANY_CHECK', 'COMPANY_CHECK'),
                                              ('GUARANTEED_FUNDS', 'GUARANTEED_FUNDS'),
                                              ('PERSONAL_CHECK', 'PERSONAL_CHECK'),
                                              ], default='ANY', string="FedEx Collection Type",
                                             help="FedEx Collection Type")

    fedex_shipping_label_stock_type = fields.Selection([
        # These values display a thermal format label
        ('PAPER_4X6', 'Paper 4X6 '),
        ('PAPER_4X8', 'Paper 4X8'),
        ('PAPER_4X9', 'Paper 4X9'),

        # These values display a plain paper format shipping label
        ('PAPER_7X4.75', 'Paper 7X4.75'),
        ('PAPER_8.5X11_BOTTOM_HALF_LABEL', 'Paper 8.5X11 Bottom Half Label'),
        ('PAPER_8.5X11_TOP_HALF_LABEL', 'Paper 8.5X11 Top Half Label'),
        ('PAPER_LETTER', 'Paper Letter'),

        # These values for Stock Type label
        ('STOCK_4X6', 'Stock 4X6'),
        ('STOCK_4X6.75_LEADING_DOC_TAB', 'Stock 4X6.75 Leading Doc Tab'),
        ('STOCK_4X6.75_TRAILING_DOC_TAB', 'Stock 4X6.75 Trailing Doc Tab'),
        ('STOCK_4X8', 'Stock 4X8'),
        ('STOCK_4X9_LEADING_DOC_TAB', 'Stock 4X9 Leading Doc Tab'),
        ('STOCK_4X9_TRAILING_DOC_TAB', 'Stock 4X9 Trailing Doc Tab')], string="Label Stock Type",
        help="Specifies the type of paper (stock) on which a document will be printed.")
    fedex_shipping_label_file_type = fields.Selection([('DPL', 'DPL'),
                                                       ('EPL2', 'EPL2'),
                                                       ('PDF', 'PDF'),
                                                       ('PNG', 'PNG'),
                                                       ('ZPLII', 'ZPLII')], string="Label File Type")
    fedex_onerate = fields.Boolean("Want To Use FedEx OneRate Service?", default=False)
    fedex_third_party_account_number = fields.Char(copy=False, string='FexEx Third-Party Account Number',
                                                   help="Please Enter the Third Party account number")
    is_cod = fields.Boolean('COD')

    # Stamps Fields
    stamps_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")

    stamps_package_type = fields.Selection([('Postcard', 'Postcard'),
                                            ('Letter', 'Letter'),
                                            ('Flat', 'Flat'),
                                            ('Package', 'Package'),
                                            ('Thick Envelope', 'Thick Envelope'),
                                            ('Package', 'Package'),
                                            ('Small Flat Rate Box', 'Small Flat Rate Box'),
                                            ('Flat Rate Box', 'Flat Rate Box'),
                                            ('Large Flat Rate Box', 'Large Flat Rate Box'),
                                            ('Flat Rate Envelope', 'Flat Rate Envelope'),
                                            ('Flat Rate Padded Envelope', 'Flat Rate Padded Envelope'),
                                            ('Large Package', 'Large Package'),
                                            ('Oversized Package', 'Oversized Package'),
                                            ('Regional Rate Box A', 'Regional Rate Box A'),
                                            ('Regional Rate Box B', 'Regional Rate Box B'),
                                            ('Regional Rate Box C', 'Regional Rate Box C'),
                                            ('Legal Flat Rate Envelope', 'Legal Flat Rate Envelope')],
                                           string="Stamps.com Package Type", help="Stamps.com provide the package")

    stam_service_info = fields.Selection([('US-FC', 'US-FC'),
                                          ('US-MM', 'US-MM'),
                                          ('US-PP', 'US-PP'),
                                          ('US-PM', 'US-PM'),
                                          ('US-XM', 'US-XM'),
                                          ('US-EMI', 'US-EMI'),
                                          ('US-PMI', 'US-PMI'),
                                          ('US-FCI', 'US-FCI'),
                                          ('US-LM', 'US-LM'),
                                          ('US-CM', 'US-CM'),
                                          ('US-PS', 'US-PS'),
                                          ('US-LM', 'US-LM'),
                                          ('DHL-PE', 'DHL-PE'),
                                          ('DHL-PG', 'DHL-PG'),
                                          ('DHL-PPE', 'DHL-PPE'),
                                          ('DHL-PPG', 'DHL-PPG'),
                                          ('DHL-BPME', 'DHL-BPME'),
                                          ('DHL-BPMG', 'DHL-BPMG'),
                                          ('DHL-MPE', 'DHL-MPE'),
                                          ('DHL-MPG', 'DHL-MPG')], string="Stamps.com Service Type",
                                         help="Stamps.com provide the package")
    # dhl fields
    dhl_service_type = fields.Selection([('0', '0-LOGISTICS SERVICES'),
                                         ('1', '1-DOMESTIC EXPRESS 12:00'),
                                         ('2', '2-B2C'),
                                         ('3', '3-B2C'),
                                         ('4', '4-JETLINE'),
                                         ('5', '5-SPRINTLINE'),
                                         ('7', '7-EXPRESS EASY'),
                                         ('8', '8-EXPRESS EASY'),
                                         ('9', '9-EUROPACK'),
                                         ('A', 'A-AUTO REVERSALS'),
                                         ('B', 'B-BREAKBULK EXPRESS'),
                                         ('C', 'C-MEDICAL EXPRESS'),
                                         ('D', 'D-EXPRESS WORLDWIDE'),
                                         ('E', 'E-EXPRESS 9:00'),
                                         ('F', 'F-FREIGHT WORLDWIDE'),
                                         ('G', 'G-DOMESTIC ECONOMY SELECT'),
                                         ('H', 'H-ECONOMY SELECT'),
                                         ('I', 'I-DOMESTIC EXPRESS 9:00'),
                                         ('J', 'J-JUMBO BOX'),
                                         ('K', 'K-EXPRESS 9:00'),
                                         ('L', 'L-EXPRESS 10:30'),
                                         ('M', 'M-EXPRESS 10:30'),
                                         ('N', 'N-DOMESTIC EXPRESS'),
                                         ('O', 'O-DOMESTIC EXPRESS 10:30'),
                                         ('P', 'P-EXPRESS WORLDWIDE'),
                                         ('Q', 'Q-MEDICAL EXPRESS'),
                                         ('R', 'R-GLOBALMAIL BUSINESS'),
                                         ('S', 'S-SAME DAY'),
                                         ('T', 'T-EXPRESS 12:00'),
                                         ('U', 'U-EXPRESS WORLDWIDE'),
                                         ('V', 'V-EUROPACK'),
                                         ('W', 'W-ECONOMY SELECT'),
                                         ('X', 'X-EXPRESS ENVELOPE'),
                                         ('Y', 'Y-EXPRESS 12:00'),
                                         ('Z', 'Z-Destination Charges')], string="Service Type",
                                        help="Shipping Services those are accepted by DHL")
    dhl_droppoff_type = fields.Selection([('DD', 'Door to Door'),
                                          ('DA', 'Door to Airport'),
                                          ('DC', 'Door to Door non-compliant')],
                                         string="Drop-off Type",
                                         help="Identifies the method by which the package is to be tendered to DHL.")
    dhl_weight_uom = fields.Selection([('LB', 'LB'),
                                       ('KG', 'KG')], string="Weight UOM",
                                      help="Weight UOM of the Shipment. If select the weight UOM KG than package dimension consider Centimeter (CM), select the weight UOM LB than package dimension consider Inch (IN).")
    dhl_default_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    dhl_shipping_label_type = fields.Selection([
        ('8X4_A4_PDF', '8X4_A4_PDF'),
        ('8X4_thermal', '8X4_thermal'),
        ('8X4_A4_TC_PDF', '8X4_A4_TC_PDF'),
        ('6X4_thermal', '6X4_thermal'),
        ('6X4_A4_PDF', '6X4_A4_PDF'),
        ('8X4_CI_PDF', '8X4_CI_PDF'),
        ('8X4_CI_thermal', '8X4_CI_thermal'),
        ('8X4_RU_A4_PDF', '8X4_RU_A4_PDF'),
        ('6X4_PDF', '6X4_PDF'),
        ('8X4_PDF', '8X4_PDF')
    ], default='8X4_A4_PDF', string="Label Stock Type",
        help="Specifies the type of paper (stock) on which a document will be printed.")
    dhl_shipping_label_file_type = fields.Selection([
        ('PDF', 'PDF'),
        ('EPL2', 'EPL2'),
        ('ZPL2', 'ZPL2'),
        ('LP2', 'LP2')], default="PDF", string="Label File Type", help="Specifies the type of lable formate.")
    dhl_region_code = fields.Selection([('AP', 'Asia Pacific'), ('EU', 'Europe'), ('AM', 'Americas')],
                                       string="Region Code",
                                       help="Indicates the shipment to be route to the specific region.")
    # gls fields
    gls_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")

    gls_product_info = fields.Selection([('Parcel', 'PARCEL'), ('Express', 'EXPRESS'), ('Freight', 'FREIGHT')],
                                        string="GLS Product Info",
                                        help="The referenced product group must be available to the shipper that is referenced within the request")

    gls_service_info = fields.Selection([('service_cash', 'service_cash'),
                                         ('service_pickandship', 'service_pickandship'),
                                         ('service_pickandreturn', 'service_pickandreturn'),

                                         ('service_addonliability', 'service_addonliability'),
                                         ('service_deliveryatwork', 'service_deliveryatwork'),
                                         ('service_deposit', 'service_deposit'),

                                         ('service_hazardousgoods', 'service_hazardousgoods'),
                                         ('service_exchange', 'service_exchange'),
                                         ('service_saturday_1000', 'service_saturday_1000'),

                                         ('service_guaranteed24', 'service_guaranteed24'),
                                         ('service_shopreturn', 'service_shopreturn'),
                                         ('service_0800', 'service_0800'),

                                         ('service_0900', 'service_0900'),
                                         ('service_1000', 'service_1000'),
                                         ('service_1200', 'service_1200'),

                                         ('service_intercompany', 'service_intercompany'),
                                         ('service_directshop', 'service_directshop'),
                                         ('service_smsservice', 'service_smsservice'),

                                         ('service_ident', 'service_ident'),
                                         ('service_identpin', 'service_identpin'),
                                         ('service_shopdelivery', 'service_shopdelivery'),

                                         ('service_preadvice', 'service_preadvice'),
                                         ('service_saturday_1200', 'service_saturday_1200'),
                                         ('service_Saturday', 'service_Saturday'),

                                         ('service_thinkgreen', 'service_thinkgreen'),
                                         ('service_exworks', 'service_exworks'),

                                         ('service_tyre', 'service_tyre'),
                                         ('service_flexdelivery', 'service_flexdelivery'),
                                         ('service_pickpack', 'service_pickpack'),

                                         ('service_documentreturn', 'service_documentreturn'),
                                         ('service_1300', 'service_1300'),
                                         ('service_addresseeonly', 'service_addresseeonly')
                                         ],
                                        string="GLS Service Type",
                                        help="The referenced product group must be available to the shipper that is referenced within the request")

    # UPS Fields
    ups_service_type = fields.Selection([('01', '01-Next Day Air'),
                                         ('02', '02-2nd Day Air'),
                                         ('03', '03-Ground'),
                                         ('12', '12-3 Day Select'),
                                         ('13', '13-Next Day Air Saver'),
                                         ('14', '14-UPS Next Day Air Early'),
                                         ('59', '59-2nd Day Air A.M.'),
                                         ('07', '07-Worldwide Express'),
                                         ('08', '08-Worldwide Expedited'),
                                         ('11', '11-Standard'),
                                         ('54', '54-Worldwide Express Plus'),
                                         ('65', '65-Saver'),
                                         ('96', '96-UPS Worldwide Express Freight')], string="Service Type")
    ups_weight_uom = fields.Selection([('LBS', 'LBS-Pounds'),
                                       ('KGS', 'KGS-Kilograms'),
                                       ('OZS', 'OZS-Ounces')], string="Weight UOM", help="Weight UOM of the Shipment")
    ups_default_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    ups_lable_print_methods = fields.Selection([('GIF', 'GIF'),
                                                ('EPL', 'EPL2'),
                                                ('ZPL', 'ZPL'),
                                                ('SPL', 'SPL'),
                                                ('STAR', 'STARPL')], string="Label File Type",
                                               help="Specifies the type of lable formate.", default="GIF")

    ups_request_option = fields.Selection([('1', '1 A list of locations'),
                                           ('8', '8 All available additional services'),
                                           ('16', '16 All available program types'),
                                           ('24', '24 All available additional services and program types'),
                                           ('32', '32 All available retail locations'),
                                           ('40', '40 All available retail locations and additional services'),
                                           ('48', '48 All available retail locations and program types'),
                                           ('56',
                                            '56 All available retail locations, program types, and additional services'),
                                           ('64', '64 UPS Access Point Search')], string="Ups Request Option",
                                          help="The RequestOption element is used to define the type of location information that will be provided.")

    ups_measurement_code = fields.Selection([('MI', 'MI Miles'), ('KM ', 'KM Kilometers')], help="UPS Measurement")
    ups_service_code = fields.Selection([('01', '01 Ground'),
                                         ('02', '02 Air'),
                                         ('03', '03 Express'),
                                         ('04', '04 Standard'),
                                         ('05', '05 International')], string="Ups Service Code",
                                        help="Container that contains the service information such as Ground/Air")
    delivery_type_ups = fields.Selection(
        [('fixed', 'UPS Fixed Price'), ('base_on_rule', 'UPS Based on Rules')],
        string='UPS Pricing',
        default='fixed')
    use_fix_shipping_rate = fields.Boolean(default=False, string="Fix Shipping Rate")
    location_required = fields.Boolean('Location Required')

    # Fedex method code
    @api.onchange('fedex_default_product_packaging_id', 'fedex_service_type')
    def fedex_onchange_service_and_package(self):
        self.fedex_onerate = False

    def do_address_validation(self, address):
        """
        Call to get the validated address from Fedex or Classification : Can be used to determine the address classification to figure out if Residential fee should apply.
        values are return in classification : MIXED, RESIDENTIAL, UNKNOWN, BUSINESS
        use address validation services, client need to request fedex to enable this service for his account.
        By default, The service is disable and you will receive authentication failed.
        """
        try:
            FedexConfig = self.company_id.get_fedex_api_object()
            avs_request = FedexAddressValidationRequest(FedexConfig)
            address_to_validate = avs_request.create_wsdl_object_of_type('AddressToValidate')
            street_lines = []
            if address.street:
                street_lines.append(address.street)
            if address.street2:
                street_lines.append(address.street2)
            address_to_validate.Address.StreetLines = street_lines
            address_to_validate.Address.City = address.city
            if address.state_id:
                address_to_validate.Address.StateOrProvinceCode = address.state_id.code
            address_to_validate.Address.PostalCode = address.zip
            if address.country_id:
                address_to_validate.Address.CountryCode = address.country_id.code
            avs_request.add_address(address_to_validate)
            avs_request.send_request()
            response = basic_sobject_to_dict(avs_request.response)
            if response.get('AddressResults'):
                return response['AddressResults'][0]  # Classification
        except FedexError as ERROR:
            raise ValidationError(ERROR.value)
        except FedexFailure as ERROR:
            raise ValidationError(ERROR.value)
        except Exception as e:
            raise ValidationError(e)

    def prepare_shipment_request(self, instance, request_obj, shipper, recipient, package_type, order):
        self.ensure_one()
        # If you wish to have transit data returned with your request you
        request_obj.ReturnTransitAndCommit = True
        request_obj.RequestedShipment.ShipTimestamp = datetime.now().replace(microsecond=0).isoformat()
        request_obj.RequestedShipment.DropoffType = self.fedex_droppoff_type
        request_obj.RequestedShipment.ServiceType = self.fedex_service_type
        request_obj.RequestedShipment.PackagingType = package_type

        # Shipper's address
        residential = True
        if instance.use_address_validation_service:
            validated_address = self.do_address_validation(shipper)
            residential = validated_address.get('Classification') != 'BUSINESS'

        request_obj.RequestedShipment.Shipper.Contact.PersonName = shipper.name if not shipper.is_company else ''
        request_obj.RequestedShipment.Shipper.Contact.CompanyName = shipper.name if shipper.is_company else ''
        request_obj.RequestedShipment.Shipper.Contact.PhoneNumber = shipper.phone
        request_obj.RequestedShipment.Shipper.Address.StreetLines = shipper.street and shipper.street2 and [
            shipper.street, shipper.street2] or [shipper.street]
        request_obj.RequestedShipment.Shipper.Address.City = shipper.city or None
        request_obj.RequestedShipment.Shipper.Address.StateOrProvinceCode = shipper.state_id and shipper.state_id.code or None
        request_obj.RequestedShipment.Shipper.Address.PostalCode = shipper.zip
        request_obj.RequestedShipment.Shipper.Address.CountryCode = shipper.country_id.code
        request_obj.RequestedShipment.Shipper.Address.Residential = residential

        # Recipient address
        residential = False
        if instance.use_address_validation_service:
            validated_address = self.do_address_validation(recipient)
            residential = validated_address.get('Classification') != 'BUSINESS'

        request_obj.RequestedShipment.Recipient.Contact.PersonName = recipient.name if not recipient.is_company else ''
        request_obj.RequestedShipment.Recipient.Contact.CompanyName = recipient.name if recipient.is_company else ''
        request_obj.RequestedShipment.Recipient.Contact.PhoneNumber = recipient.mobile or recipient.phone
        request_obj.RequestedShipment.Recipient.Address.StreetLines = recipient.street and recipient.street2 and [
            recipient.street, recipient.street2] or [recipient.street]
        request_obj.RequestedShipment.Recipient.Address.City = recipient.city
        request_obj.RequestedShipment.Recipient.Address.StateOrProvinceCode = recipient.state_id and recipient.state_id.code or ''
        request_obj.RequestedShipment.Recipient.Address.PostalCode = recipient.zip
        request_obj.RequestedShipment.Recipient.Address.CountryCode = recipient.country_id.code
        request_obj.RequestedShipment.Recipient.Address.Residential = residential
        # include estimated duties and taxes in rate quote, can be ALL or NONE
        request_obj.RequestedShipment.EdtRequestType = 'NONE'

        request_obj.RequestedShipment.ShippingChargesPayment.Payor.ResponsibleParty.AccountNumber = order.fedex_third_party_account_number_sale_order if order.fedex_third_party_account_number_sale_order else instance.fedex_account_number
        request_obj.RequestedShipment.ShippingChargesPayment.PaymentType = "THIRD_PARTY" if order.fedex_third_party_account_number_sale_order else "SENDER"
        return request_obj

    def manage_fedex_packages(self, rate_request, weight, number=1):
        package_weight = rate_request.create_wsdl_object_of_type('Weight')
        package_weight.Value = weight
        package_weight.Units = self.fedex_weight_uom
        package = rate_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package.Weight = package_weight
        if self.fedex_default_product_packaging_id.shipper_package_code == 'YOUR_PACKAGING':
            package.Dimensions.Length = self.fedex_default_product_packaging_id.packaging_length
            package.Dimensions.Width = self.fedex_default_product_packaging_id.width
            package.Dimensions.Height = self.fedex_default_product_packaging_id.height
            package.Dimensions.Units = 'IN' if self.fedex_weight_uom == 'LB' else 'CM'
        package.PhysicalPackaging = 'BOX'
        package.GroupPackageCount = 1
        if number:
            package.SequenceNumber = number
        return package

    def add_fedex_package(self, ship_request, weight, package_count, number=1, master_tracking_id=False,
                          package_id=False):
        package_weight = ship_request.create_wsdl_object_of_type('Weight')
        package_weight.Value = weight
        package_weight.Units = self.fedex_weight_uom
        package = ship_request.create_wsdl_object_of_type('RequestedPackageLineItem')
        package.Weight = package_weight
        if self.fedex_default_product_packaging_id.shipper_package_code == 'YOUR_PACKAGING':
            package.Dimensions.Length = package_id and package_id.package_type_id.packaging_length if package_id and package_id.package_type_id.packaging_length else self.fedex_default_product_packaging_id.packaging_length
            package.Dimensions.Width = package_id and package_id.package_type_id.width if package_id and package_id.package_type_id.width else self.fedex_default_product_packaging_id.width
            package.Dimensions.Height = package_id and package_id.package_type_id.height if package_id and package_id.package_type_id.height else self.fedex_default_product_packaging_id.height
            package.Dimensions.Units = 'IN' if self.fedex_weight_uom == 'LB' else 'CM'
        package.PhysicalPackaging = 'BOX'
        if number:
            package.SequenceNumber = number
        ship_request.RequestedShipment.RequestedPackageLineItems = package
        ship_request.RequestedShipment.TotalWeight.Value = weight
        ship_request.RequestedShipment.PackageCount = package_count
        if master_tracking_id:
            ship_request.RequestedShipment.MasterTrackingId.TrackingIdType = 'FEDEX'
            ship_request.RequestedShipment.MasterTrackingId.TrackingNumber = master_tracking_id
        return ship_request

    def fedex_shipping_provider_rate_shipment(self, orders):
        res = []
        shipping_charge = 0.0
        for order in orders:
            order_lines_without_weight = order.order_line.filtered(
                lambda line_item: not line_item.product_id.type in ['service',
                                                                    'digital'] and not line_item.product_id.weight and not line_item.is_delivery)
            for order_line in order_lines_without_weight:
                raise ValidationError("Please define weight in product : \n %s" % (order_line.product_id.name))

            # Shipper and Recipient Address
            shipper_address = order.warehouse_id.partner_id
            recipient_address = order.partner_shipping_id
            shipping_credential = self.company_id

            # check sender Address
            if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
                raise ValidationError("Please Define Proper Sender Address!")

            # check Receiver Address
            if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
                raise ValidationError("Please Define Proper Recipient Address!")

            total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
            total_weight = self.company_id.weight_convertion(self.fedex_weight_uom, total_weight)
            max_weight = self.company_id.weight_convertion(self.fedex_weight_uom,
                                                           self.fedex_default_product_packaging_id.max_weight)
            try:
                # This is the object that will be handling our request.
                FedexConfig = self.company_id.get_fedex_api_object(self.prod_environment)
                rate_request = FedexRateServiceRequest(FedexConfig)
                package_type = self.fedex_default_product_packaging_id.shipper_package_code
                rate_request = self.prepare_shipment_request(shipping_credential, rate_request, shipper_address,
                                                             recipient_address, package_type, order)
                rate_request.RequestedShipment.PreferredCurrency = order.currency_id.name
                if max_weight and total_weight > max_weight:
                    total_package = int(total_weight / max_weight)
                    last_package_weight = total_weight % max_weight

                    for index in range(1, total_package + 1):
                        package = self.manage_fedex_packages(rate_request, max_weight, index)
                        rate_request.add_package(package)
                    if last_package_weight:
                        index = total_package + 1
                        package = self.manage_fedex_packages(rate_request, last_package_weight, index)
                        rate_request.add_package(package)
                #                         rate_request.RequestedShipment.RequestedPackageLineItems.append(package)
                else:
                    total_package = 1
                    package = self.manage_fedex_packages(rate_request, total_weight)
                    rate_request.add_package(package)
                #                 rate_request.RequestedShipment.TotalWeight.Value = total_weight
                #                 rate_request.RequestedShipment.PackageCount = total_package
                if self.fedex_onerate:
                    rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['FEDEX_ONE_RATE']
                if self.is_cod and not order.fedex_third_party_account_number_sale_order:
                    rate_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['COD']
                    cod_vals = {'Amount': order.amount_total,
                                'Currency': order.company_id.currency_id.name}
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = cod_vals
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType.value = "%s" % (
                        self.fedex_collection_type)

                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PersonName = shipper_address.name if not shipper_address.is_company else ''
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.CompanyName = shipper_address.name if shipper_address.is_company else ''
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PhoneNumber = shipper_address.phone
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StreetLines = shipper_address.street and shipper_address.street2 and [
                        shipper_address.street, shipper_address.street2] or [shipper_address.street]
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.City = shipper_address.city or None
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StateOrProvinceCode = shipper_address.state_id and shipper_address.state_id.code or None
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.PostalCode = shipper_address.zip
                    rate_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.CountryCode = shipper_address.country_id.code

                rate_request.send_request()
            except FedexError as ERROR:
                raise ValidationError(ERROR.value)
                # raise ValidationError(ERROR.value)
            except FedexFailure as ERROR:
                raise ValidationError(ERROR.value)
                # raise ValidationError(ERROR.value)
            except Exception as e:
                raise ValidationError(e)
                # raise ValidationError(e)
            for shipping_service in rate_request.response.RateReplyDetails:
                for rate_info in shipping_service.RatedShipmentDetails:
                    shipping_charge = float(rate_info.ShipmentRateDetail.TotalNetFedExCharge.Amount)
                    shipping_charge_currency = rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency
                    if order.currency_id.name != rate_info.ShipmentRateDetail.TotalNetFedExCharge.Currency:
                        rate_currency = self.env['res.currency'].search([('name', '=', shipping_charge_currency)],
                                                                        limit=1)
                        if rate_currency:
                            shipping_charge = rate_currency.compute(float(shipping_charge), order.currency_id)
        return {'success': True, 'price': float(shipping_charge) + self.add_custom_margin, 'error_message': False,
                'warning_message': False}

    def get_fedex_tracking_and_label(self, ship_request, is_cod=False):
        self.ensure_one()
        CompletedPackageDetails = ship_request.response.CompletedShipmentDetail.CompletedPackageDetails[0]
        shipping_charge = 0.0
        if hasattr(CompletedPackageDetails, 'PackageRating'):
            shipping_charge = CompletedPackageDetails.PackageRating.PackageRateDetails[0].NetCharge.Amount
        else:
            _logger.warn('Unable to get shipping rate!')
        tracking_number = CompletedPackageDetails.TrackingIds[0].TrackingNumber
        ascii_label_data = ship_request.response.CompletedShipmentDetail.CompletedPackageDetails[0].Label.Parts[0].Image
        cod_details = False
        cod_error_message = False
        try:
            if is_cod:
                cod_details = ship_request.response.CompletedShipmentDetail.AssociatedShipments[0] and \
                              ship_request.response.CompletedShipmentDetail.AssociatedShipments[0].Label and \
                              ship_request.response.CompletedShipmentDetail.AssociatedShipments[0].Label.Parts[0] and \
                              ship_request.response.CompletedShipmentDetail.AssociatedShipments[0].Label.Parts[
                                  0].Image or False
                if cod_details:
                    cod_details = binascii.a2b_base64(cod_details)
        except Exception as e:
            cod_error_message = e
        label_binary_data = binascii.a2b_base64(ascii_label_data)
        return shipping_charge, tracking_number, label_binary_data, cod_details, cod_error_message

    # require changes in this module

    def fedex_shipping_provider_send_shipping(self, pickings):
        res = []
        fedex_master_tracking_id = False
        for picking in pickings:
            if not (picking.sale_id and picking.sale_id.fedex_bill_by_third_party_sale_order):
                picking.get_fedex_rate()
            exact_price = 0.0
            traking_number = []
            attachments = []
            total_bulk_weight = self.company_id.weight_convertion(self.fedex_weight_uom, picking.weight_bulk)
            package_count = len(picking.package_ids)
            if total_bulk_weight:
                package_count += 1
            shipping_credential = self.company_id

            if not self._context.get('use_fedex_return', False) and picking.picking_type_code == "incoming":
                shipping_data = {
                    'exact_price': picking.carrier_price,
                    'tracking_number': picking.carrier_tracking_ref}
                return [shipping_data]

            if picking.picking_type_code == "incoming":
                shipper_address = picking.partner_id
                recipient_address = picking.picking_type_id.warehouse_id.partner_id
            else:
                recipient_address = picking.partner_id
                shipper_address = picking.picking_type_id.warehouse_id.partner_id
            try:
                FedexConfig = self.company_id.get_fedex_api_object(self.prod_environment)
                ship_request = FedexProcessShipmentRequest(FedexConfig)

                # checking for Identical packages in same shipment.
                # picking.check_packages_are_identical()

                package_type = self.fedex_default_product_packaging_id.shipper_package_code
                ship_request = self.prepare_shipment_request(shipping_credential, ship_request, shipper_address,
                                                             recipient_address, package_type, picking.sale_id)

                # Supported LabelFormatType by fedex
                # COMMON2D, FEDEX_FREIGHT_STRAIGHT_BILL_OF_LADING, LABEL_DATA_ONLY, VICS_BILL_OF_LADING
                ship_request.RequestedShipment.LabelSpecification.LabelFormatType = 'COMMON2D'
                ship_request.RequestedShipment.LabelSpecification.ImageType = self.fedex_shipping_label_file_type
                ship_request.RequestedShipment.LabelSpecification.LabelStockType = self.fedex_shipping_label_stock_type
                #                 if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST', 'INTERNATIONAL_PRIORITY']:
                #                     ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['ELECTRONIC_TRADE_DOCUMENTS']
                #                     ship_request.RequestedShipment.SpecialServicesRequested.EtdDetail.RequestedDocumentCopies = ['COMMERCIAL_INVOICE']
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.ShippingDocumentTypes = ['COMMERCIAL_INVOICE']
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.CertificateOfOrigin.DocumentFormat.ImageType = "PDF"
                #                     ship_request.RequestedShipment.ShippingDocumentSpecification.CertificateOfOrigin.DocumentFormat.StockType = ['PAPER_LETTER']
                # This indicates if the top or bottom of the label comes out of the printer first.
                # BOTTOM_EDGE_OF_TEXT_FIRST, TOP_EDGE_OF_TEXT_FIRST
                ship_request.RequestedShipment.LabelSpecification.LabelPrintingOrientation = 'BOTTOM_EDGE_OF_TEXT_FIRST'

                # Specify the order in which the labels will be returned : SHIPPING_LABEL_FIRST, SHIPPING_LABEL_LAST
                ship_request.RequestedShipment.LabelSpecification.LabelOrder = "SHIPPING_LABEL_FIRST"

                for sequence, package in enumerate(picking.package_ids, start=1):
                    # A multiple-package shipment (MPS) consists of two or more packages shipped to the same recipient.
                    # The first package in the shipment request is considered the master package.

                    # Note: The maximum number of packages in an MPS request is 200.
                    package_weight = self.company_id.weight_convertion(self.fedex_weight_uom, package.shipping_weight)
                    ship_request = self.add_fedex_package(ship_request, package_weight, package_count, number=sequence,
                                                          master_tracking_id=fedex_master_tracking_id,
                                                          package_id=package)
                    # ship_request = self.add_fedex_package(picking,ship_request, package_weight, package_count, number=sequence, master_tracking_id=fedex_master_tracking_id,package=package)
                    if self.fedex_onerate:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['FEDEX_ONE_RATE']
                    if self.is_cod and picking.sale_id and picking.sale_id.fedex_third_party_account_number_sale_order == False:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['COD']
                        cod_vals = {'Amount': picking.sale_id.amount_total + picking.carrier_price,
                                    'Currency': picking.sale_id.company_id.currency_id.name}
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = cod_vals
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType.value = "%s" % (
                            self.fedex_collection_type)

                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PersonName = shipper_address.name if not shipper_address.is_company else ''
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.CompanyName = shipper_address.name if shipper_address.is_company else ''
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PhoneNumber = shipper_address.phone
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StreetLines = shipper_address.street and shipper_address.street2 and [
                            shipper_address.street, shipper_address.street2] or [shipper_address.street]
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.City = shipper_address.city or None
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StateOrProvinceCode = shipper_address.state_id and shipper_address.state_id.code or None
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.PostalCode = shipper_address.zip
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.CountryCode = shipper_address.country_id.code

                    ship_request.send_request()
                    shipping_charge, tracking_number, label_binary_data, cod_details, cod_error_message = self.get_fedex_tracking_and_label(
                        ship_request,
                        self.is_cod and picking.sale_id and picking.sale_id.fedex_third_party_account_number_sale_order == False)
                    picking.message_post(body=cod_error_message if cod_error_message else "")
                    if cod_details:
                        attachments.append(
                            ('Fedex_COD_RETURN%s.%s' % (tracking_number, self.fedex_shipping_label_file_type),
                             cod_details))
                    attachments.append(
                        ('Fedex-%s.%s' % (tracking_number, self.fedex_shipping_label_file_type), label_binary_data))
                    exact_price += float(shipping_charge)
                    traking_number.append(tracking_number)
                    package.custom_tracking_number = tracking_number
                    if sequence == 1 and package_count > 1:
                        fedex_master_tracking_id = ship_request.response.CompletedShipmentDetail.MasterTrackingId.TrackingNumber
                if total_bulk_weight:
                    order = picking.sale_id
                    if self.fedex_service_type in ['INTERNATIONAL_ECONOMY', 'INTERNATIONAL_FIRST',
                                                   'INTERNATIONAL_PRIORITY'] or (
                            picking.partner_id.country_id.code == 'IN' and picking.picking_type_id.warehouse_id.partner_id.country_id.code == 'IN'):
                        company = order.company_id or picking.company_id or self.env.user.company_id
                        order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
                        commodity_country_of_manufacture = picking.picking_type_id.warehouse_id.partner_id.country_id.code
                        commodity_weight_units = self.fedex_weight_uom
                        total_commodities_amount = 0.0
                        for operation in picking.move_line_ids:
                            commodity_amount = order_currency._convert(operation.product_id.list_price, order_currency,
                                                                       company, order.date_order or fields.Date.today())
                            total_commodities_amount += (commodity_amount * operation.qty_done)
                            Commodity = ship_request.create_wsdl_object_of_type('Commodity')
                            Commodity.UnitPrice.Currency = order_currency.name
                            Commodity.UnitPrice.Amount = commodity_amount
                            Commodity.NumberOfPieces = '1'
                            Commodity.CountryOfManufacture = commodity_country_of_manufacture
                            Commodity.Weight.Units = commodity_weight_units
                            Commodity.Weight.Value = self.company_id.weight_convertion(self.fedex_weight_uom,
                                                                                       operation.product_id.weight * operation.qty_done)
                            Commodity.Description = operation.product_id.name
                            Commodity.Quantity = operation.qty_done
                            Commodity.QuantityUnits = 'EA'
                            ship_request.RequestedShipment.CustomsClearanceDetail.Commodities.append(Commodity)
                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.PaymentType = "THIRD_PARTY" if order.fedex_bill_by_third_party_sale_order else "SENDER"
                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.AccountNumber = order.fedex_third_party_account_number_sale_order if order.fedex_bill_by_third_party_sale_order else self.company_id and self.company_id.fedex_account_number
                        ship_request.RequestedShipment.CustomsClearanceDetail.DutiesPayment.Payor.ResponsibleParty.Address.CountryCode = picking.picking_type_id.warehouse_id.partner_id.country_id.code
                        ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Amount = total_commodities_amount
                        ship_request.RequestedShipment.CustomsClearanceDetail.CustomsValue.Currency = picking.sale_id.currency_id.name or picking.company_id.currency_id.name

                    ship_request = self.add_fedex_package(ship_request, total_bulk_weight, 1,
                                                          number=1,
                                                          master_tracking_id=fedex_master_tracking_id, package_id=False)
                    if self.fedex_onerate:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['FEDEX_ONE_RATE']
                    if self.is_cod and order.fedex_bill_by_third_party_sale_order == False:
                        ship_request.RequestedShipment.SpecialServicesRequested.SpecialServiceTypes = ['COD']
                        cod_vals = {'Amount': picking.sale_id.amount_total + picking.carrier_price,
                                    'Currency': picking.sale_id.company_id.currency_id.name}
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodCollectionAmount = cod_vals
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CollectionType.value = "%s" % (
                            self.fedex_collection_type)

                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PersonName = shipper_address.name if not shipper_address.is_company else ''
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.CompanyName = shipper_address.name if shipper_address.is_company else ''
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Contact.PhoneNumber = shipper_address.phone
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StreetLines = shipper_address.street and shipper_address.street2 and [
                            shipper_address.street, shipper_address.street2] or [shipper_address.street]
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.City = shipper_address.city or None
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.StateOrProvinceCode = shipper_address.state_id and shipper_address.state_id.code or None
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.PostalCode = shipper_address.zip
                        ship_request.RequestedShipment.SpecialServicesRequested.CodDetail.CodRecipient.Address.CountryCode = shipper_address.country_id.code

                    ship_request.send_request()
                    shipping_charge, tracking_number, label_binary_data, cod_details, cod_error_message = self.get_fedex_tracking_and_label(
                        ship_request, self.is_cod and order.fedex_bill_by_third_party_sale_order == False)
                    picking.message_post(body=cod_error_message if cod_error_message else "")
                    if cod_details:
                        attachments.append(
                            ('Fedex_COD_RETURN%s.%s' % (tracking_number, self.fedex_shipping_label_file_type),
                             cod_details))

                    exact_price += float(shipping_charge)
                    traking_number.append(tracking_number)
                    attachments.append(
                        ('Fedex-%s.%s' % (tracking_number, self.fedex_shipping_label_file_type), label_binary_data))
                msg = (_('<b>Shipment created!</b><br/>'))
                picking.message_post(body=msg, attachments=attachments)
            except FedexError as ERROR:
                raise ValidationError(ERROR.value)
            except FedexFailure as ERROR:
                raise ValidationError(ERROR.value)
            except Exception as e:
                raise ValidationError(e)
            res = res + [{'exact_price': exact_price + self.add_custom_margin,
                          'tracking_number': fedex_master_tracking_id if fedex_master_tracking_id else ",".join(
                              traking_number)}]
        return res

    def fedex_shipping_provider_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = "https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber="
            res = '%s %s' % (link, picking.carrier_tracking_ref)
        return res

    def fedex_shipping_provider_cancel_shipment(self, picking):
        try:
            FedexConfig = self.company_id.get_fedex_api_object(self.prod_environment)
            delete_request = FedexDeleteShipmentRequest(FedexConfig)
            delete_request.DeletionControlType = "DELETE_ALL_PACKAGES"
            delete_request.TrackingId.TrackingNumber = picking.carrier_tracking_ref.split(',')[
                0]  # master tracking number
            delete_request.TrackingId.TrackingIdType = 'FEDEX'
            delete_request.send_request()
            assert delete_request.response.HighestSeverity in ['SUCCESS', 'WARNING'], \
                "%s : %s" % (
                    picking.carrier_tracking_ref.split(',')[0], delete_request.response.Notifications[0].Message)
        except FedexError as ERROR:
            raise ValidationError(ERROR.value)
        except FedexFailure as ERROR:
            raise ValidationError(ERROR.value)
        except Exception as e:
            raise ValidationError(e)

    # stamps.com methods
    def stamps_rate_shipment(self, orders):
        for order in orders:
            order_lines_without_weight = order.order_line.filtered(
                lambda line_item: not line_item.product_id.type in ['service',
                                                                    'digital'] and not line_item.product_id.weight and not line_item.is_delivery)
            for order_line in order_lines_without_weight:
                return {'success': False, 'price': 0.0,
                        'error_message': "Please define weight in product : \n %s" % (order_line.product_id.name),
                        'warning_message': False}

            # Shipper and Recipient Address
            sender_id = order.warehouse_id.partner_id
            receiver_id = order.partner_shipping_id

            # check sender Address
            if not sender_id.zip or not sender_id.city or not sender_id.country_id:
                return {'success': False, 'price': 0.0,
                        'error_message': "Please Define Proper Sender Address!",
                        'warning_message': False}

            # check Receiver Address
            if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
                return {'success': False, 'price': 0.0,
                        'error_message': "Please Define Proper Recipient Address!",
                        'warning_message': False}

            total_weight = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0

            pound_for_kg = 2.20462
            uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
            if uom_id.name == 'lb':
                weight_lb = round(total_weight, 3)
            else:
                weight_lb = round(total_weight * pound_for_kg, 3)

            master_node = etree.Element('Envelope')
            master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"

            submater_node = etree.SubElement(master_node, 'Body')
            root_node = etree.SubElement(submater_node, "GetRates")
            root_node.attrib['xmlns'] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
            # etree.SubElement(root_node, "Authenticator").text = self.company_id and self.company_id.stamps_authenticator

            shipment_data = etree.SubElement(root_node, "Credentials")

            etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
                    self.company_id and self.company_id.stamps_integrator_id)
            etree.SubElement(shipment_data, "Username").text = "%s" % (
                    self.company_id and self.company_id.stamps_user_name)
            etree.SubElement(shipment_data, "Password").text = "%s" % (
                    self.company_id and self.company_id.stamps_password)

            shipment_data = etree.SubElement(root_node, "Rate")
            from_tag = etree.SubElement(shipment_data, "From")
            etree.SubElement(from_tag, "State").text = "%s" % (sender_id.state_id.code)
            etree.SubElement(from_tag, "ZIPCode").text = "%s" % (sender_id.zip)
            etree.SubElement(from_tag, "Country").text = "%s" % (sender_id.country_id.code)

            to_tag = etree.SubElement(shipment_data, "To")
            etree.SubElement(to_tag, "Country").text = "%s" % (receiver_id.country_id.code)
            etree.SubElement(shipment_data, "WeightLb").text = "%s" % (int(weight_lb))
            etree.SubElement(shipment_data, "PackageType").text = "%s" % (self.stamps_package_type)

            current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")  # '2020-10-01'
            etree.SubElement(shipment_data, "ShipDate").text = current_date
            etree.SubElement(root_node, 'Carrier')
            request_data = etree.tostring(master_node)
            url = "%s" % (self.company_id.stamps_api_url)
            stamp_shipping_charge_obj = self.env['stamp.shipping.charge']
            headers = {
                'SOAPAction': "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/GetRates",
                'Content-Type': 'text/xml; charset="utf-8"'
            }
            try:
                _logger.info("Stamps.com Request Data : %s" % (request_data))
                result = requests.post(url=url, data=request_data, headers=headers)
            except Exception as e:
                return {'success': False, 'price': 0.0, 'error_message': e,
                        'warning_message': False}

            if result.status_code != 200:
                return {'success': False, 'price': 0.0,
                        'error_message': "Rate Request Data Invalid! %s " % result.content,
                        'warning_message': False}
            api = Response(result)
            result = api.dict()

            _logger.info("Stamps.com Rate Response Data : %s" % (result))
            existing_records = stamp_shipping_charge_obj.sudo().search([('sale_order_id', '=', order and order.id)])
            existing_records.sudo().unlink()

            res = result.get('Envelope', {}).get('Body', {}).get('GetRatesResponse', {}).get('Rates')
            if res:
                for rate in res.get('Rate'):
                    _logger.info("In for Loop")
                    stamp_service_name = rate.get('ServiceType')
                    stamp_service_charge = rate.get('Amount')
                    stamp_service_shipping_day = rate.get('DeliverDays')
                    stamp_shipping_charge_obj.sudo().create(
                        {'stamp_service_name': stamp_service_name,
                         'stamp_service_rate': stamp_service_charge,
                         'stamp_service_delivery_date': stamp_service_shipping_day,
                         'sale_order_id': order and order.id,

                         }
                    )
                stamp_service_charge_id = stamp_shipping_charge_obj.sudo().search(
                    [('sale_order_id', '=', order and order.id)], order="stamp_service_rate", limit=1)
                order.stamp_shipping_charge_id = stamp_service_charge_id and stamp_service_charge_id.id
                return {'success': True,
                        'price': stamp_service_charge_id and stamp_service_charge_id.stamp_service_rate or 0.0,
                        'error_message': False, 'warning_message': False}
            if not res:
                return {'success': False, 'price': 0.0, 'error_message': "Error Response %s" % (result),
                        'warning_message': False}

    def stamps_label_request_data(self,picking=False):
        sender_id = picking.picking_type_id and picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.partner_id
        receiver_id = picking.partner_id

        pound_for_kg = 2.20462
        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if uom_id.name == 'lbs':
            weight_lb = round(picking.shipping_weight, 3)
        else :
            weight_lb = round(picking.shipping_weight * pound_for_kg, 3)


        # check sender Address
        if not sender_id.zip or not sender_id.city or not sender_id.country_id:
            raise ValidationError("Please Define Proper Sender Address!")

        # check Receiver Address
        if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")

        master_node = etree.Element('Envelope')
        master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, 'Body')
        root_node = etree.SubElement(submater_node, "CreateIndicium")
        root_node.attrib['xmlns'] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
        # etree.SubElement(root_node, "Authenticator").text = self.company_id and self.company_id.stamps_authenticator

        shipment_data = etree.SubElement(root_node, "Credentials")

        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
                self.company_id and self.company_id.stamps_integrator_id)
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.company_id and self.company_id.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.company_id and self.company_id.stamps_password)
        etree.SubElement(root_node, "IntegratorTxID").text = "%s" % (
                self.company_id and self.company_id.stamps_integrator_id)

        shipment_data = etree.SubElement(root_node, "Rate")

        shipper_adress = etree.SubElement(shipment_data, "From")

        etree.SubElement(shipper_adress, "FullName").text = "%s" % (sender_id.name)
        etree.SubElement(shipper_adress, "Address1").text = "%s" % (sender_id.street)
        etree.SubElement(shipper_adress, "City").text = "%s" % (sender_id.city)
        etree.SubElement(shipper_adress, "State").text = "%s" % (
                sender_id.state_id and sender_id.state_id.code or "")
        etree.SubElement(shipper_adress, "ZIPCode").text = "%s" % (sender_id.zip)
        etree.SubElement(shipper_adress, "Country").text = "%s" % (
                sender_id.country_id and sender_id.country_id.code or "")
        etree.SubElement(shipper_adress, "PhoneNumber").text = "%s" % (sender_id.phone)
        etree.SubElement(shipper_adress, "EmailAddress").text = "%s" % (sender_id.email)

        receiver_adress = etree.SubElement(shipment_data, "To")
        etree.SubElement(receiver_adress, "FullName").text = "%s" % (receiver_id.name)
        etree.SubElement(receiver_adress, "Address1").text = "%s" % (receiver_id.street)
        etree.SubElement(receiver_adress, "City").text = "%s" % (receiver_id.city)
        etree.SubElement(receiver_adress, "State").text = "%s" % (
                receiver_id.state_id and receiver_id.state_id.code or "")
        etree.SubElement(receiver_adress, "ZIPCode").text = "%s" % (receiver_id.zip)
        etree.SubElement(receiver_adress, "Country").text = "%s" % (
                receiver_id.country_id and receiver_id.country_id.code or "")
        etree.SubElement(receiver_adress, "PhoneNumber").text = "%s" % (receiver_id.phone)
        etree.SubElement(receiver_adress, "EmailAddress").text = "%s" % (receiver_id.email)

        etree.SubElement(shipment_data, "ServiceType").text = "%s" % (
            picking.sale_id.stamp_shipping_charge_id.stamp_service_name if picking.sale_id.stamp_shipping_charge_id else self.stam_service_info)

        etree.SubElement(shipment_data, "WeightLb").text = "%s" % (weight_lb)
        etree.SubElement(shipment_data, "PackageType").text = "%s" % (self.stamps_package_type)
        etree.SubElement(shipment_data, "Length").text = "%s" % (
                    self.stamps_packaging_id and self.stamps_packaging_id.packaging_length or 0.0)
        etree.SubElement(shipment_data, "Width").text = "%s" % (
                    self.stamps_packaging_id and self.stamps_packaging_id.width or 0.0)
        etree.SubElement(shipment_data, "Height").text = "%s" % (
                    self.stamps_packaging_id and self.stamps_packaging_id.height or 0.0)
        # current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")
        etree.SubElement(shipment_data, "ShipDate").text = str(picking.scheduled_date.strftime("%Y-%m-%d"))

        etree.SubElement(root_node, "ImageType").text = "Png"
        return etree.tostring(master_node)

    @api.model
    def stamps_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            try:
                request_data = self.stamps_label_request_data(picking)
                url = "%s"%(self.company_id.stamps_api_url)
                headers = {
                    'SOAPAction': "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/CreateIndicium",
                    'Content-Type': 'text/xml; charset="utf-8"'
                }
                try:
                    _logger.info("Stamps.com Request Data : %s" % (request_data))
                    result = requests.post(url=url, data=request_data, headers=headers)
                except Exception as e:
                    raise ValidationError(e)

                if result.status_code != 200:
                    raise ValidationError(_("Label Request Data Invalid! %s ")%(result.content))
                api = Response(result)
                result = api.dict()

                _logger.info("Stamps.com Shipment Response Data : %s" % (result))

                res = result.get('Envelope', {}).get('Body', {}).get('CreateIndiciumResponse', {})
                if not res:
                    raise ValidationError(_("Error Response %s") % (result))
                TrackingNumber = res.get('TrackingNumber')
                StampsTxID = res.get('StampsTxID')
                stamps_URL = res.get('URL')
                Amount = res.get('Rate').get('Amount')

                message = (_("Label created!<br/> <b>Label Tracking Number : </b>%s<br/> <b> Parcel Number : %s") % (TrackingNumber,StampsTxID))
                picking.message_post(body=message)

                picking.carrier_tracking_ref = TrackingNumber
                picking.stamps_label_url = stamps_URL
                picking.stamps_tx_id = StampsTxID

                shipping_data = {
                    'exact_price': float(Amount) or 0.0,
                    'tracking_number': TrackingNumber}
                response += [shipping_data]
            except Exception as e:
                raise ValidationError(e)
        return response

    def stamps_cancel_shipment(self, picking):
        master_node = etree.Element('Envelope')
        master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, 'Body')
        root_node = etree.SubElement(submater_node, "CancelIndicium")
        root_node.attrib['xmlns'] = "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111"
        shipment_data = etree.SubElement(root_node, "Credentials")
        etree.SubElement(shipment_data, "IntegrationID").text = "%s" % (
                self.company_id and self.company_id.stamps_integrator_id)
        etree.SubElement(shipment_data, "Username").text = "%s" % (self.company_id and self.company_id.stamps_user_name)
        etree.SubElement(shipment_data, "Password").text = "%s" % (self.company_id and self.company_id.stamps_password)
        etree.SubElement(root_node, "TrackingNumber").text = "%s" % (picking.carrier_tracking_ref)
        try:
            request_data = etree.tostring(master_node)
            url = "%s" % (self.company_id.stamps_api_url)
            headers = {
                'SOAPAction': "http://stamps.com/xml/namespace/2021/01/swsim/SwsimV111/CancelIndicium",
                'Content-Type': 'text/xml; charset="utf-8"'
            }
            try:
                _logger.info("Stamps.com Request Data : %s" % (request_data))
                result = requests.post(url=url, data=request_data, headers=headers)
            except Exception as e:
                raise ValidationError(e)

            if result.status_code != 200:
                raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
            api = Response(result)
            result = api.dict()
            if result.get('Envelope').get('Body').get('Fault'):
                raise ValidationError(result.get('Envelope').get('Body').get('Fault'))
            else:
                _logger.info("Stamps.com cancel Shipment Response Data : %s" % (result))

        except Exception as e:
            raise ValidationError(e)

    def stamps_get_tracking_link(self, pickings):
        return "https://www.stamps.com/shipstatus/?confirmation=%s" % pickings.carrier_tracking_ref


    # dhl express methods
    @api.model
    def dhl_express_rate_shipment(self, orders):
        res = []
        price = 0.0
        for order in orders:
            shipment_weight = self.dhl_default_product_packaging_id and self.dhl_default_product_packaging_id.max_weight or 0.0

            shipper_address = order.warehouse_id and order.warehouse_id.partner_id
            recipient_address = order.partner_shipping_id

            total_weight = self.convert_weight(sum(
                [(line.product_id.weight * line.product_uom_qty) for line in orders.order_line if
                 not line.is_delivery]))
            total_weight = round(total_weight, 3)
            declared_value = round(order.amount_untaxed, 2)
            declared_currency = order.currency_id and order.currency_id.name
            shipping_dict = self.dhl_get_shipping_rate(shipper_address, recipient_address, total_weight, packages=False,
                                                       picking_bulk_weight=False, declared_value=declared_value, \
                                                       declared_currency=declared_currency, request_type="rate_request",
                                                       company_id=order.company_id)

            if shipping_dict['error_message']:
                return {'success': False, 'price': 0.0, 'error_message': shipping_dict['error_message'],
                        'warning_message': False}

            currency_code = shipping_dict.get('CurrencyCode')
            shipping_charge = shipping_dict.get('ShippingCharge')

            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            price = rate_currency.compute(float(shipping_charge), order.currency_id)
            res += [float(price)]
        return {'success': True, 'price': float(price), 'error_message': False, 'warning_message': False}

    dhl_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centremetres')], string="Dimension Unit",
                                          help="Dimension Unit of the Shipment.")
    dhl_is_dutiable = fields.Boolean(string="Is Dutiable", default=False,
                                     help="IsDutiable element indicates whether the shipment is dutiable or not.")

    dhl_duty_payment_type = fields.Selection([('S', 'Sender'), ('R', 'Receiver')], string="DutyPayment Type",
                                             help="DutyPaymentType element contains the method of duty and tax payment.")

    @api.model
    def get_dhl_api_object(self, environment):
        api = DHL_API(environment, timeout=500)
        return api

    def convert_weight(self, shipping_weight):

        pound_for_kg = 2.20462

        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.dhl_weight_uom == "LB":
            return round(shipping_weight * pound_for_kg, 3)
        else:
            return shipping_weight

    @api.model
    def dhl_get_shipping_rate(self, shipper_address, recipient_address, total_weight, picking_bulk_weight,
                              packages=False, declared_value=False, \
                              declared_currency=False, request_type=False, company_id=False):
        res = {'ShippingCharge': 0.0, 'CurrencyCode': False, 'error_message': False}
        # built request data
        api = self.get_dhl_api_object(self.prod_environment)
        root_node = etree.Element("GetQuote")
        header_node = etree.SubElement(root_node, "Request")
        header_node = etree.SubElement(header_node, "ServiceHeader")
        etree.SubElement(header_node, "SiteID").text = self.company_id and self.company_id.dhl_express_userid
        etree.SubElement(header_node, "Password").text = self.company_id and self.company_id.dhl_express_password
        from_node = etree.SubElement(root_node, "From")
        etree.SubElement(from_node, "CountryCode").text = shipper_address.country_id and shipper_address.country_id.code
        etree.SubElement(from_node, "Postalcode").text = shipper_address.zip
        etree.SubElement(from_node, "City").text = shipper_address.city
        bkg_details_node = etree.SubElement(root_node, "BkgDetails")
        etree.SubElement(bkg_details_node,
                         "PaymentCountryCode").text = shipper_address.country_id and shipper_address.country_id.code
        etree.SubElement(bkg_details_node, "Date").text = time.strftime("%Y-%m-%d")
        etree.SubElement(bkg_details_node, "ReadyTime").text = time.strftime('PT%HH%MM')
        if self.dhl_weight_uom == "KG":
            etree.SubElement(bkg_details_node, "DimensionUnit").text = "CM"
        else:
            etree.SubElement(bkg_details_node, "DimensionUnit").text = "IN"
        etree.SubElement(bkg_details_node, "WeightUnit").text = self.dhl_weight_uom
        pieces_detail = etree.SubElement(bkg_details_node, "Pieces")
        if packages:
            for package in packages:
                product_weight = self.convert_weight(package.shipping_weight)
                shipping_box = package.package_type_id or self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (package.id)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (product_weight)
            if picking_bulk_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (1)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (picking_bulk_weight)
        else:
            max_weight = self.convert_weight(
                self.dhl_default_product_packaging_id and self.dhl_default_product_packaging_id.max_weight)
            if not request_type == "rate_request" or not max_weight and total_weight > max_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (1)
                # etree.SubElement(piece_node, 'PackageTypeCode').text = "BOX"
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (total_weight)
                # if max_weight and total_weight > max_weight:
            else:
                if total_weight == 0.0:
                    raise ValidationError(_('please define a weight of product'))
                num_of_packages = int(ceil(total_weight / max_weight))
                total_package_weight = total_weight / num_of_packages
                total_package_weight = round(total_package_weight, 3)
                while (num_of_packages > 0):
                    shipping_box = self.dhl_default_product_packaging_id
                    piece_node = etree.SubElement(pieces_detail, "Piece")
                    # etree.SubElement(piece_node, 'PackageTypeCode').text = "BOX"
                    etree.SubElement(piece_node, "PieceID").text = "%s" % (num_of_packages)
                    etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                    etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                    etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                    etree.SubElement(piece_node, "Weight").text = "%s" % (total_package_weight)
                    num_of_packages = num_of_packages - 1

        if self.dhl_is_dutiable:
            etree.SubElement(bkg_details_node, "IsDutiable").text = "Y"
        else:
            etree.SubElement(bkg_details_node, "IsDutiable").text = "N"
        # Valid values are: TD : for air products, DD : for road products, AL : for both air and road products.
        etree.SubElement(bkg_details_node, "NetworkTypeCode").text = "AL"
        QtdShp_node = etree.SubElement(bkg_details_node, "QtdShp")
        etree.SubElement(QtdShp_node, "GlobalProductCode").text = self.dhl_service_type
        to_node = etree.SubElement(root_node, "To")
        etree.SubElement(to_node,
                         "CountryCode").text = recipient_address.country_id and recipient_address.country_id.code
        etree.SubElement(to_node, "Postalcode").text = recipient_address.zip
        etree.SubElement(to_node, "City").text = recipient_address.city
        if self.dhl_is_dutiable:
            dutiable_node = etree.SubElement(root_node, "Dutiable")
            etree.SubElement(dutiable_node, "DeclaredCurrency").text = "%s" % (declared_currency)
            etree.SubElement(dutiable_node, "DeclaredValue").text = "%s" % (declared_value)
        try:
            api.execute('DCTRequest', etree.tostring(root_node).decode('utf-8'))
            results = api.response.dict()
            _logger.info("DHL Express rate Shipment response Data: %s" % (results))
        except Exception as e:
            res['error_message'] = e
            return res
        product_details = results.get('DCTResponse', {}).get('GetQuoteResponse', {}).get('BkgDetails', {}).get('QtdShp',
                                                                                                               {})
        if isinstance(product_details, dict):
            product_details = [product_details]
        for product in product_details:
            if product.get('GlobalProductCode') == self.dhl_service_type:
                if product.get('ShippingCharge', False):
                    res.update({'ShippingCharge': product.get('ShippingCharge', 0.0),
                                'CurrencyCode': product.get('CurrencyCode', False)})
                else:
                    res['error_message'] = (_("Shipping service is not available for this location."))
            else:
                res['error_message'] = (_("No shipping service available!"))
        return res

    @api.model
    def dhl_express_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            total_weight = self.convert_weight(picking.shipping_weight)
            total_weight = round(total_weight, 2)
            total_bulk_weight = self.convert_weight(picking.weight_bulk)
            total_bulk_weight = round(total_bulk_weight, 2)
            total_value = sum([(line.product_uom_qty * line.product_id.list_price) for line in pickings.move_lines])
            recipient = picking.partner_id
            shipper = picking.picking_type_id and picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.partner_id
            # carrier = picking.carrier_id
            picking_company_id = picking.company_id

            api = self.get_dhl_api_object(
                self.prod_environment)  # self.shipping_instance_id.get_dhl_api_object(self.prod_environment)
            shipment_request = etree.Element("ShipmentRequest")
            request_node = etree.SubElement(shipment_request, "Request")
            request_node = etree.SubElement(request_node, "ServiceHeader")
            etree.SubElement(request_node, "MessageTime").text = datetime.strftime(datetime.now(pytz.utc),
                                                                                   "%Y-%m-%dT%H:%M:%S")
            etree.SubElement(request_node, "MessageReference").text = "1234567890123456789012345678901"
            etree.SubElement(request_node,
                             "SiteID").text = self.company_id and self.company_id.dhl_express_userid  # self.shipping_instance_id and self.shipping_instance_id.userid
            etree.SubElement(request_node,
                             "Password").text = self.company_id and self.company_id.dhl_express_password  # self.shipping_instance_id and self.shipping_instance_id.password
            if self.dhl_region_code:
                etree.SubElement(shipment_request, "RegionCode").text = self.dhl_region_code
            etree.SubElement(shipment_request, "RequestedPickupTime").text = "Y"
            etree.SubElement(shipment_request, "LanguageCode").text = "en"
            etree.SubElement(shipment_request, "PiecesEnabled").text = "Y"
            billing_node = etree.SubElement(shipment_request, "Billing")
            etree.SubElement(billing_node, "ShipperAccountNumber").text = "%s" % (
                self.company_id.dhl_express_account_number)
            etree.SubElement(billing_node, "ShippingPaymentType").text = "S"
            if self.dhl_is_dutiable:
                etree.SubElement(billing_node, "DutyPaymentType").text = "%s" % (self.dhl_duty_payment_type or "")
            receiver_node = etree.SubElement(shipment_request, "Consignee")
            etree.SubElement(receiver_node, "CompanyName").text = recipient.name
            etree.SubElement(receiver_node, "AddressLine").text = recipient.street
            if recipient.street2:
                etree.SubElement(receiver_node, "AddressLine").text = recipient.street2
            etree.SubElement(receiver_node, "City").text = recipient.city
            if recipient.state_id:
                etree.SubElement(receiver_node, "Division").text = recipient.state_id and recipient.state_id.name
                etree.SubElement(receiver_node,
                                 "DivisionCode").text = recipient.state_id and recipient.state_id.code or ""
            etree.SubElement(receiver_node, "PostalCode").text = recipient.zip
            etree.SubElement(receiver_node,
                             "CountryCode").text = recipient.country_id and recipient.country_id.code or ""
            etree.SubElement(receiver_node, "CountryName").text = recipient.country_id and recipient.country_id.name
            contact_node = etree.SubElement(receiver_node, "Contact")
            etree.SubElement(contact_node, "PersonName").text = recipient.name
            etree.SubElement(contact_node, "PhoneNumber").text = recipient.phone
            etree.SubElement(contact_node, "Email").text = recipient.email
            reference_node = etree.SubElement(shipment_request, "Reference")
            etree.SubElement(reference_node,
                             "ReferenceID").text = picking.sale_id and picking.sale_id.name or picking.name
            if self.dhl_is_dutiable:
                dutiable_node = etree.SubElement(shipment_request, "Dutiable")
                total_value = '%.2f' % (total_value)
                etree.SubElement(dutiable_node, "DeclaredValue").text = "%s" % (total_value)
                etree.SubElement(dutiable_node,
                                 "DeclaredCurrency").text = picking.sale_id and picking.sale_id.currency_id and picking.sale_id.currency_id.name or picking_company_id.currency_id and picking_company_id.currency_id.name
            shipment_information_node = etree.SubElement(shipment_request, "ShipmentDetails")
            if total_bulk_weight:
                number_of_piece = len(picking.package_ids) + 1
                etree.SubElement(shipment_information_node, "NumberOfPieces").text = "%s" % (number_of_piece or 1)
            else:
                etree.SubElement(shipment_information_node, "NumberOfPieces").text = "%s" % (
                        len(picking.package_ids) or 1)
            pieces_node = etree.SubElement(shipment_information_node, "Pieces")
            # added the packages first and then the misc items to ship
            for package in picking.package_ids:
                product_weight = self.convert_weight(package.shipping_weight)
                product_weight = round(product_weight, 3)
                shipping_box = package.package_type_id or self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_node, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (package.name or "")
                etree.SubElement(piece_node, "PackageType").text = "{}".format(shipping_box.shipper_package_code or ' ')
                etree.SubElement(piece_node, "Weight").text = "%s" % (product_weight)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
            if total_bulk_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_node, "Piece")
                etree.SubElement(piece_node, "PieceID").text = str(1)
                etree.SubElement(piece_node, "PackageType").text = "{}".format(shipping_box.shipper_package_code or ' ')
                if picking.package_ids:
                    etree.SubElement(piece_node, "Weight").text = "%s" % (total_bulk_weight)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
            etree.SubElement(shipment_information_node, "Weight").text = "%s" % (total_weight)
            etree.SubElement(shipment_information_node, "WeightUnit").text = "L" if self.dhl_weight_uom == 'LB' else "K"
            etree.SubElement(shipment_information_node, "GlobalProductCode").text = self.dhl_service_type
            etree.SubElement(shipment_information_node, "LocalProductCode").text = self.dhl_service_type
            etree.SubElement(shipment_information_node, "Date").text = time.strftime("%Y-%m-%d")
            etree.SubElement(shipment_information_node, "Contents").text = str(picking.note) or ""
            etree.SubElement(shipment_information_node, "DoorTo").text = self.dhl_droppoff_type
            if self.dhl_weight_uom == 'KG':
                etree.SubElement(shipment_information_node, "DimensionUnit").text = "C"
            else:
                etree.SubElement(shipment_information_node, "DimensionUnit").text = "I"
            etree.SubElement(shipment_information_node,
                             "CurrencyCode").text = picking_company_id.currency_id and picking_company_id.currency_id.name
            sender_node = etree.SubElement(shipment_request, "Shipper")
            etree.SubElement(sender_node,
                             "ShipperID").text = self.company_id.dhl_express_userid  # self.shipping_instance_id and self.shipping_instance_id.dhl_account_number
            etree.SubElement(sender_node, "CompanyName").text = picking_company_id.name
            etree.SubElement(sender_node, "AddressLine").text = shipper.street
            if picking.partner_id.street2:
                etree.SubElement(sender_node, "AddressLine").text = shipper.street2
            etree.SubElement(sender_node, "City").text = shipper.city
            etree.SubElement(sender_node, "PostalCode").text = shipper.zip
            etree.SubElement(sender_node, "CountryCode").text = shipper.country_id and shipper.country_id.code
            etree.SubElement(sender_node, "CountryName").text = shipper.country_id and shipper.country_id.name
            contact_node = etree.SubElement(sender_node, "Contact")
            etree.SubElement(contact_node, "PersonName").text = shipper.name
            etree.SubElement(contact_node, "PhoneNumber").text = shipper.phone
            etree.SubElement(shipment_request, "LabelImageFormat").text = self.dhl_shipping_label_file_type
            label_node = etree.SubElement(shipment_request, "Label")
            etree.SubElement(label_node, "LabelTemplate").text = self.dhl_shipping_label_type
            try:

                api.execute('ShipmentRequest', etree.tostring(shipment_request).decode('utf-8'), version=str(5.25))
                results = api.response.dict()
                _logger.info("DHL Express send Shipment response Data: %s" % (results))
            except Exception as e:
                raise ValidationError(e)
            ShipmentResponse = results.get('ShipmentResponse', {})
            tracking_no = ShipmentResponse.get('AirwayBillNumber', False)
            lable_image = results.get('ShipmentResponse', {}).get('LabelImage', {}).get('OutputImage', False)
            label_binary_data = binascii.a2b_base64(str(lable_image))
            declared_currency = picking.company_id and picking.company_id.currency_id and picking.company_id.currency_id.name
            packages = picking.package_ids
            res = self.dhl_get_shipping_rate(shipper, recipient, total_weight, picking_bulk_weight=total_bulk_weight,
                                             packages=packages, declared_value=total_value, \
                                             declared_currency=declared_currency, request_type="label_request",
                                             company_id=picking.company_id)
            # convert currency In Sale order Currency.
            currency_code = res.get('CurrencyCode')
            shipping_charge = res.get('ShippingCharge')
            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            exact_price = rate_currency.compute(float(shipping_charge),
                                                picking.sale_id.currency_id or picking.company_id.currency_id)
            message_ept = (_("Shipment created!<br/> <b>Shipment Tracking Number : </b>%s") % (tracking_no))
            picking.message_post(body=message_ept, attachments=[
                ('DHL Label-%s.%s' % (tracking_no, self.dhl_shipping_label_file_type), label_binary_data)])
            shipping_data = {
                'exact_price': exact_price,
                'tracking_number': tracking_no}
            response += [shipping_data]
        return response

    def dhl_express_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = "http://www.dhl.com/en/express/tracking.html?AWB="
            res = '%s %s' % (link, picking.carrier_tracking_ref)
        return res

    def dhl_express_cancel_shipment(self, picking):
        raise ValidationError(_("You can not cancel DHL shipment."))

    #gls methods

    def gls_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def gls_label_request_data(self, picking=False):
        sender_id = picking.picking_type_id and picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.partner_id
        receiver_id = picking.partner_id

        #
        if not sender_id.email:
            raise ValidationError(_("Please define the email address of sender"))

        if not receiver_id.email:
            raise ValidationError(_("Please define the email address of receiver"))

        # check sender Address
        if not sender_id.zip or not sender_id.city or not sender_id.country_id:
            raise ValidationError("Please Define Proper Sender Address!")

        # check Receiver Address
        if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")

        master_node = etree.Element('Envelope')
        master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, 'Body')
        root_node = etree.SubElement(submater_node, "ShipmentRequestData")
        root_node.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/ShipmentProcessing/types"
        shipment_data = etree.SubElement(root_node, "Shipment")
        current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")
        etree.SubElement(shipment_data, "ShipmentReference").text = "%s" % (picking.name)
        etree.SubElement(shipment_data, "ShippingDate").text = current_date
        etree.SubElement(shipment_data, "IncotermCode").text = ""
        etree.SubElement(shipment_data, "Identifier").text = ""
        etree.SubElement(shipment_data, "Product").text = "%s" % (self.gls_product_info)

        consignee_data = etree.SubElement(shipment_data, "Consignee")
        consignee_id = etree.SubElement(consignee_data, "ConsigneeID")
        consignee_id.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        consignee_id.text = "%s" % (receiver_id.id)
        cost_center = etree.SubElement(consignee_data, "CostCenter")
        cost_center.text = "%s" % (receiver_id.id)
        cost_center.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        consignee_address = etree.SubElement(consignee_data, "Address")
        consignee_address.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        etree.SubElement(consignee_address, "Name1").text = "%s" % (receiver_id.name)
        etree.SubElement(consignee_address, "Name2").text = ""
        etree.SubElement(consignee_address, "Name3").text = ""
        etree.SubElement(consignee_address, "CountryCode").text = "%s" % (
                receiver_id.country_id and receiver_id.country_id.code or "")
        etree.SubElement(consignee_address, "Province").text = "%s" % (
                receiver_id.state_id and receiver_id.state_id.code or "")
        etree.SubElement(consignee_address, "ZIPCode").text = "%s" % (receiver_id.zip)
        etree.SubElement(consignee_address, "City").text = "%s" % (receiver_id.city)
        etree.SubElement(consignee_address, "Street").text = "%s" % (receiver_id.street)
        etree.SubElement(consignee_address, "StreetNumber").text = ""
        etree.SubElement(consignee_address, "eMail").text = "%s" % (receiver_id.email)
        etree.SubElement(consignee_address, "ContactPerson").text = "%s" % (receiver_id.name)
        etree.SubElement(consignee_address, "FixedLinePhonenumber").text = ""
        etree.SubElement(consignee_address, "MobilePhoneNumber").text = "%s" % (receiver_id.phone)

        shipper_data = etree.SubElement(shipment_data, "Shipper")
        contact_id = etree.SubElement(shipper_data, "ContactID")
        contact_id.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        contact_id.text = "%s" % (self.company_id and self.company_id.gls_contact_id)
        shipper_adress = etree.SubElement(shipper_data, "AlternativeShipperAddress")
        shipper_adress.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        etree.SubElement(shipper_adress, "Name1").text = "%s" % (sender_id.name)
        etree.SubElement(shipper_adress, "Name2").text = ""
        etree.SubElement(shipper_adress, "Name3").text = ""
        etree.SubElement(shipper_adress, "CountryCode").text = "%s" % (
                sender_id.country_id and sender_id.country_id.code or "")
        etree.SubElement(shipper_adress, "Province").text = "%s" % (
                sender_id.state_id and sender_id.state_id.code or "")
        etree.SubElement(shipper_adress, "ZIPCode").text = "%s" % (sender_id.zip)
        etree.SubElement(shipper_adress, "City").text = "%s" % (sender_id.city)
        etree.SubElement(shipper_adress, "Street").text = "%s" % (sender_id.street)
        etree.SubElement(shipper_adress, "StreetNumber").text = ""
        etree.SubElement(shipper_adress, "eMail").text = "%s" % (sender_id.email)
        etree.SubElement(shipper_adress, "ContactPerson").text = "%s" % (sender_id.name)
        etree.SubElement(shipper_adress, "FixedLinePhonenumber").text = ""
        etree.SubElement(shipper_adress, "MobilePhoneNumber").text = "%s" % (sender_id.phone)

        ShipmentUnit = etree.SubElement(shipment_data, "ShipmentUnit")
        etree.SubElement(ShipmentUnit, "ShipmentUnitReference").text = "%s" % (picking.name)
        etree.SubElement(ShipmentUnit, "Weight").text = "%s" % (picking.shipping_weight)
        shipment_service = etree.SubElement(ShipmentUnit, "Service")
        if self.gls_service_info == 'service_hazardousgoods':
            HazardousGoods = etree.SubElement(shipment_service, "HazardousGoods")
            HazardousGoods.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
            etree.SubElement(HazardousGoods, "ServiceName").text = "service_hazardousgoods"
            HazardousGood = etree.SubElement(HazardousGoods, "HazardousGood")
            etree.SubElement(HazardousGood, "GLSHazNo").text = "%s" % (picking.id)
            etree.SubElement(HazardousGood, "Weight").text = "%s" % (picking.shipping_weight)

        Service_info = etree.SubElement(shipment_data, "Service")
        if self.gls_service_info:
            Service_name = etree.SubElement(Service_info, "Service")
            Service_name.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
            etree.SubElement(Service_name, "ServiceName").text = "%s" % (self.gls_service_info)
        if picking.sale_id.gls_location_id:
            shop_delivery = etree.SubElement(Service_info, "ShopDelivery")
            shop_delivery.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
            etree.SubElement(shop_delivery, "ServiceName").text = "service_shopdelivery"
            etree.SubElement(shop_delivery, "ParcelShopID").text = "%s" % picking.sale_id.gls_location_id.gls_location_parcelshopid

        PrintingOptions = etree.SubElement(root_node, "PrintingOptions")
        ReturnLabels = etree.SubElement(PrintingOptions, "ReturnLabels")
        etree.SubElement(ReturnLabels, "TemplateSet").text = "NONE"
        etree.SubElement(ReturnLabels, "LabelFormat").text = "PDF"
        return etree.tostring(master_node)

    @api.model
    def gls_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            try:
                request_data = self.gls_label_request_data(picking)
                data = "%s:%s" % (
                    self.company_id and self.company_id.gls_user_id, self.company_id and self.company_id.gls_password)
                encode_data = base64.b64encode(data.encode("utf-8"))
                authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
                url = "%s/backend/ShipmentProcessingService/ShipmentProcessingPortType" % (self.company_id.gls_api_url)
                headers = {
                    'Authorization': authrization_data,
                    'SOAPAction': "http://fpcs.gls-group.eu/v1/createShipment",
                    'Content-Type': 'text/xml; charset="utf-8"'
                }
                try:
                    _logger.info("GSL Request Data : %s" % (request_data))
                    result = requests.post(url=url, data=request_data, headers=headers)
                except Exception as e:
                    raise ValidationError(e)
                if result.status_code != 200:
                    raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
                api = Response(result)
                result = api.dict()
                _logger.info("GLS Shipment Response Data : %s" % (result))
                res = result.get('Envelope', {}).get('Body', {}).get('CreateParcelsResponse', {}).get('CreatedShipment',
                                                                                                      {})
                if not res:
                    raise ValidationError(_("Error Response %s") % (result))
                binary_data = res.get('PrintData', {}).get('Data')
                track_id = res.get('ParcelData', {}).get('TrackID')
                parcel_number = res.get('ParcelData', {}).get('ParcelNumber')
                binary_data = binascii.a2b_base64(str(binary_data))
                message = (_("Label created!<br/> <b>Label Tracking Number : </b>%s<br/> <b> Parcel Number : %s") % (
                    track_id, parcel_number))
                picking.message_post(body=message, attachments=[
                    ('Label-%s.%s' % (track_id, "pdf"), binary_data)])
                picking.carrier_tracking_ref = track_id
                # self.label_to_direct_printer(data=binary_data)
                # picking.print_label_in_printer(pdf_data=binary_data)
                shipping_data = {
                    'exact_price': 0.0,
                    'tracking_number': track_id}
                response += [shipping_data]
            except Exception as e:
                raise ValidationError(e)
        return response

    def gls_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = self.company_id and self.company_id.gls_tracking_url
            res = '%s%s' % (link, picking.carrier_tracking_ref)
            if not res:
                raise ValidationError("Tracking URL Is Not Set!")
        return res

    def gls_cancel_shipment(self, pickings):
        api_endpoint = pickings.company_id and pickings.company_id.gls_api_url
        api_ulr = "%s/backend/rs/shipments/cancel/%s" % (api_endpoint, pickings.carrier_tracking_ref)
        data = "%s:%s" % (
            self.company_id and self.company_id.gls_user_id, self.company_id and self.company_id.gls_password)
        encode_data = base64.b64encode(data.encode("utf-8"))
        authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
        headers = {
            'Authorization': authrization_data,
        }
        try:
            response_data = requests.post(url=api_ulr, headers=headers)
            if response_data.status_code in [200, 201]:
                response_data = response_data.json()
                result = response_data.get('result').upper()
                if result in ["CANCELLED", "CANCELLATION_PENDING"]:
                    _logger.info("Successfully cancel order")
                else:
                    raise ValidationError(response_data)
            else:
                raise ValidationError(
                    "Getting some error from %s \n response data %s" % (api_ulr, response_data.content))
        except Exception as error:
            raise ValidationError(_(error))

    #UPS Method
    def ups_shipment_accept(self, shipment_degits):
        service_root = etree.Element("ShipmentAcceptRequest")
        request_node = etree.SubElement(service_root, "Request")
        etree.SubElement(request_node, "RequestAction").text = "ShipAccept"
        etree.SubElement(request_node, "RequestOption").text = "01"
        etree.SubElement(service_root, "ShipmentDigest").text = str(shipment_degits)
        if not self.prod_environment:
            url = 'https://wwwcie.ups.com/ups.app/xml/ShipAccept'
        else:
            url = 'https://onlinetools.ups.com/ups.app/xml/ShipAccept'
        try:
            xml = etree.tostring(service_root)
            xml = xml.decode('utf-8')
            base_data = "<AccessRequest xml:lang=\"en-US\"><AccessLicenseNumber>%s</AccessLicenseNumber><UserId>%s</UserId><Password>%s</Password></AccessRequest>" % (
            self.company_id.access_license_number, self.company_id.ups_userid, self.company_id.ups_password)
            base_data += xml
            headers = {"Content-Type": "application/xml"}
            response_body = request(method='POST', url=url, data=base_data, headers=headers)
            result = {}
            if response_body.status_code == 200:
                api = Response(response_body)
                result = api.dict()
                return result
            else:
                error_code = "%s" % (response_body.status_code)
                error_message = response_body.reason
                message = error_code + " " + error_message
                raise Warning(
                    "ShipmentAcceptRequest Fail : %s \n More Information \n %s" % (message, response_body.text))
        except Exception as e:
            raise Warning(e)

    def ups_get_shipping_rate(self, shipper_address, recipient_address, total_weight, picking_bulk_weight,
                              packages=False, declared_value=False, \
                              declared_currency=False):
        res = {}
        # built request data
        api = self.company_id.get_ups_api_object(self.prod_environment, "Rate",
                                                 self.company_id.ups_userid,
                                                 self.company_id.ups_password,
                                                 self.company_id.access_license_number)
        service_root = etree.Element("RatingServiceSelectionRequest")

        request = etree.SubElement(service_root, "Request")
        etree.SubElement(request, "RequestAction").text = "Rate"
        etree.SubElement(request, "RequestOption").text = "Rate"

        shipment = etree.SubElement(service_root, "Shipment")
        etree.SubElement(shipment, "Description").text = "Rate Description"

        shipper = etree.SubElement(shipment, "Shipper")
        from_address = etree.SubElement(shipper, "Address")
        etree.SubElement(from_address, "PostalCode").text = "%s" % (shipper_address.zip)
        etree.SubElement(from_address, "CountryCode").text = "%s" % (
                    shipper_address.country_id and shipper_address.country_id.code)

        ship_to = etree.SubElement(shipment, "ShipTo")
        ship_to_address = etree.SubElement(ship_to, "Address")
        etree.SubElement(ship_to_address, "PostalCode").text = "%s" % (recipient_address.zip)
        etree.SubElement(ship_to_address, "CountryCode").text = "%s" % (
                    recipient_address.country_id and recipient_address.country_id.code)

        service_discription = etree.SubElement(shipment, "Service")
        etree.SubElement(service_discription, "Code").text = "%s" % (self.ups_service_type)

        if self.ups_service_type == '96':
            # When Calling the Rate API we pass numofpiece 1 manually when calling rate API Because When Used the 96 service must pass some piece or in sale order we have not any packages so pass manually one.
            etree.SubElement(shipment, "NumOfPieces").text = str("1")
        if self.ups_service_type in ['07', '08', '11', '54', '65', '96']:
            shipment_weight = etree.SubElement(shipment, "ShipmentTotalWeight")
            package_uom = etree.SubElement(shipment_weight, "UnitOfMeasurement")
            etree.SubElement(package_uom, "Code").text = "%s" % (self.ups_weight_uom)
            etree.SubElement(shipment_weight, "Code").text = "%s" % (total_weight)

        if packages:
            for package in packages:
                product_weight = self.company_id.weight_convertion(self.ups_weight_uom, package.shipping_weight)

                package_info = etree.SubElement(shipment, "Package")
                package_type = etree.SubElement(package_info, "PackagingType")

                etree.SubElement(package_type, "Code").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.shipper_package_code)
                package_weight = etree.SubElement(package_info, "PackageWeight")

                # dimension is condition parameter We use just in internation service
                if self.ups_service_type == '96':
                    package_dimention = etree.SubElement(package_info, "Dimensions")

                    etree.SubElement(package_dimention, "Length").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.packaging_length or "0")
                    etree.SubElement(package_dimention, "Width").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.width or "0")
                    etree.SubElement(package_dimention, "Height").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.height or "0")

                package_uom = etree.SubElement(package_weight, "UnitOfMeasurement")
                etree.SubElement(package_uom, "Code").text = "%s" % (self.ups_weight_uom)
                etree.SubElement(package_weight, "Weight").text = "%s" % (product_weight)
            if picking_bulk_weight:
                package_info = etree.SubElement(shipment, "Package")
                package_type = etree.SubElement(package_info, "PackagingType")

                etree.SubElement(package_type, "Code").text = "%s" % (
                    self.ups_default_product_packaging_id.shipper_package_code)
                package_weight = etree.SubElement(package_info, "PackageWeight")

                # dimension is condition parameter We use just in internation service
                if self.ups_service_type == '96':
                    package_dimention = etree.SubElement(package_info, "Dimensions")

                    etree.SubElement(package_dimention, "Length").text = "%s" % (
                                self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.packaging_length or "0")
                    etree.SubElement(package_dimention, "Width").text = "%s" % (
                                self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.width or "0")
                    etree.SubElement(package_dimention, "Height").text = "%s" % (
                                self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.height or "0")

                package_uom = etree.SubElement(package_weight, "UnitOfMeasurement")
                etree.SubElement(package_uom, "Code").text = "%s" % (self.ups_weight_uom)
                etree.SubElement(package_weight, "Weight").text = "%s" % (picking_bulk_weight)
        else:
            max_weight = self.company_id.weight_convertion(self.ups_weight_uom,
                                                           self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.max_weight)

            if max_weight and total_weight > max_weight:
                num_of_packages = int(ceil(total_weight / max_weight))

                total_package_weight = total_weight / num_of_packages
                while (num_of_packages > 0):
                    package_info = etree.SubElement(shipment, "Package")
                    package_type = etree.SubElement(package_info, "PackagingType")

                    etree.SubElement(package_type, "Code").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.shipper_package_code)
                    package_weight = etree.SubElement(package_info, "PackageWeight")

                    package_uom = etree.SubElement(package_weight, "UnitOfMeasurement")
                    etree.SubElement(package_uom, "Code").text = "%s" % (self.ups_weight_uom)
                    etree.SubElement(package_weight, "Weight").text = "%s" % (total_package_weight)
                    num_of_packages = num_of_packages - 1
            else:
                package_info = etree.SubElement(shipment, "Package")
                package_type = etree.SubElement(package_info, "PackagingType")
                etree.SubElement(package_type, "Code").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.shipper_package_code or "")
                package_weight = etree.SubElement(package_info, "PackageWeight")

                # dimension is condition parameter We use just in internation service
                if self.ups_service_type == '96':
                    package_dimention = etree.SubElement(package_info, "Dimensions")

                    etree.SubElement(package_dimention, "Length").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.packaging_length or "0")
                    etree.SubElement(package_dimention, "Width").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.width or "0")
                    etree.SubElement(package_dimention, "Height").text = "%s" % (
                            self.ups_default_product_packaging_id and self.ups_default_product_packaging_id.height or "0")

                package_uom = etree.SubElement(package_weight, "UnitOfMeasurement")
                etree.SubElement(package_uom, "Code").text = "%s" % (self.ups_weight_uom)
                etree.SubElement(package_weight, "Weight").text = "%s" % (total_weight)
        try:
            api.execute('RatingServiceSelectionRequest', etree.tostring(service_root))
            results = api.response.dict()
            _logger.info(results)
        except Exception as e:
            raise ValidationError(e)

        product_details = results.get('RatingServiceSelectionResponse', {}).get('RatedShipment', {})

        code = product_details.get('Service', {})
        service_code = code.get('Code')

        service_detail = product_details.get('TotalCharges', {})
        shipment_charge = service_detail.get('MonetaryValue', False)
        currency_code = service_detail.get('CurrencyCode', False)

        if service_code == self.ups_service_type:
            if shipment_charge:
                res.update({'ShippingCharge': shipment_charge or 0.0,
                            'CurrencyCode': currency_code})
                return res
            else:
                raise ValidationError(_("Shipping service is not available for this location."))
        else:
            raise ValidationError(_("No shipping service available!"))

    def check_recipient_address(self, recipient_address=False):
        if recipient_address:
            api = self.company_id.get_ups_api_object(self.prod_environment, "AV",
                                                     self.company_id and self.company_id.ups_userid,
                                                     self.company_id and self.company_id.ups_password,
                                                     self.company_id and self.company_id.access_license_number)
            service_root = etree.Element("AddressValidationRequest")

            request = etree.SubElement(service_root, "Request")
            etree.SubElement(request, "RequestAction").text = "AV"

            address = etree.SubElement(service_root, "Address")
            etree.SubElement(address, "City").text = "%s" % (recipient_address.city or "")
            etree.SubElement(address, "StateProvinceCode").text = "%s" % (
                        recipient_address.state_id and recipient_address.state_id.code or "")
            etree.SubElement(address, "PostalCode").text = "%s" % (recipient_address.zip or "")
            etree.SubElement(address, "CountryCode").text = "%s" % (
                        recipient_address.country_id and recipient_address.country_id.code or "")
            try:
                api.execute('AddressValidationRequest', etree.tostring(service_root))
                results = api.response.dict()
                _logger.info(results)
            except Exception as e:
                raise ValidationError("Address Validation Error :%s" % (e))
            response_status = results.get('AddressValidationResponse', False) and results.get(
                'AddressValidationResponse', False).get('Response', False) and results.get('AddressValidationResponse',
                                                                                           False).get('Response',
                                                                                                      False).get(
                'ResponseStatusCode')
            # response_status is success then status code is 1 otherwise 0.
            if response_status == '1':
                return True
            else:
                message = results.get('AddressValidationResponse', False) and results.get(
                    'AddressValidationResponse', False).get('Response', False) and results.get(
                    'AddressValidationResponse', False).get('Response', False).get('Error')
                raise ValidationError(message)

    def ups_shipping_provider_rate_shipment(self, orders):
        for order in orders:

            order_lines_without_weight = order.order_line.filtered(
                lambda line_item: not line_item.product_id.type in ['service',
                                                                    'digital'] and not line_item.product_id.weight and not line_item.is_delivery)
            for order_line in order_lines_without_weight:
                return {'success': False, 'price': 0.0,
                        'error_message': "Please define weight in product : \n %s" % (order_line.product_id.name),
                        'warning_message': False}

            # Shipper and Recipient Address
            shipper_address = order.warehouse_id.partner_id
            recipient_address = order.partner_shipping_id
            shipping_credential = self.company_id

            # check sender Address
            if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
                return {'success': False, 'price': 0.0, 'error_message': "Please Define Proper Sender Address!",
                        'warning_message': False}

            # check Receiver Address
            if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
                return {'success': False, 'price': 0.0, 'error_message': "Please Define Proper Recipient Address!",
                        'warning_message': False}

            # convet weight in to the delivery method's weight UOM
            total_weight = sum(
                [(line.product_id.weight * line.product_uom_qty) for line in orders.order_line if not line.is_delivery])
            total_weight = self.company_id.weight_convertion(self.ups_weight_uom, total_weight)

            declared_value = round(order.amount_untaxed, 2)
            declared_currency = order.currency_id.name

            shipping_dict = self.ups_get_shipping_rate(shipper_address, recipient_address, total_weight, packages=False,
                                                       picking_bulk_weight=False, declared_value=declared_value,
                                                       declared_currency=declared_currency)

            currency_code = shipping_dict.get('CurrencyCode')
            shipping_charge = shipping_dict.get('ShippingCharge')
            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            price = rate_currency.compute(float(shipping_charge), order.currency_id)
            order.ups_service_rate = price
            if self.use_fix_shipping_rate:
                if self.delivery_type_ups == 'fixed':
                    return self.fixed_rate_shipment(order)
                if self.delivery_type_ups == 'base_on_rule':
                    return self.base_on_rule_rate_shipment(order)

            return {'success': True, 'price': float(price) or 0.0,
                    'error_message': False, 'warning_message': False}

    @api.model
    def ups_shipping_provider_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            total_weight = self.company_id.weight_convertion(self.ups_weight_uom, picking.shipping_weight)
            total_bulk_weight = self.company_id.weight_convertion(self.ups_weight_uom, picking.weight_bulk)
            total_value = sum([(line.product_uom_qty * line.product_id.list_price) for line in pickings.move_lines])

            if picking.picking_type_code == "incoming":
                picking_company_id = picking.partner_id
                picking_carrier_id = picking.carrier_id
                picking_partner_id = picking.picking_type_id.warehouse_id.partner_id
                if picking.carrier_tracking_ref:
                    shipping_data = {
                        'exact_price': picking.carrier_price,
                        'tracking_number': picking.carrier_tracking_ref}
                    response += [shipping_data]
                    return response
            else:
                picking_partner_id = picking.partner_id
                picking_carrier_id = picking.carrier_id
                picking_company_id = picking.picking_type_id.warehouse_id.partner_id

            receiver_street = picking.sale_id.ups_shipping_location_id.street if picking.sale_id.ups_shipping_location_id.street else picking_partner_id.street or ""
            receiver_city = picking.sale_id.ups_shipping_location_id.city if picking.sale_id.ups_shipping_location_id.city else picking_partner_id.city or ""
            receiver_zip = picking.sale_id.ups_shipping_location_id.zip if picking.sale_id.ups_shipping_location_id.zip else picking_partner_id.zip or ""
            receiver_country_code = picking.sale_id.ups_shipping_location_id.country_code if picking.sale_id.ups_shipping_location_id.country_code else picking_partner_id.country_id and picking_partner_id.country_id.code or ""
            receiver_state = picking.sale_id.ups_shipping_location_id.state_code if picking.sale_id.ups_shipping_location_id.state_code else picking_partner_id.country_id and picking_partner_id.state_id.code or ""

            api = self.company_id.get_ups_api_object(self.prod_environment, "ShipConfirm",
                                                     self.company_id.ups_userid,
                                                     self.company_id.ups_password,
                                                     self.company_id.access_license_number)

            shipment_request = etree.Element("ShipmentConfirmRequest")
            request_node = etree.SubElement(shipment_request, "Request")
            etree.SubElement(request_node, "RequestAction").text = "ShipConfirm"
            etree.SubElement(request_node, "RequestOption").text = "nonvalidate"

            shipment_node = etree.SubElement(shipment_request, "Shipment")

            etree.SubElement(shipment_node, "Description").text = str(picking.note or "")

            shipper_node = etree.SubElement(shipment_node, "Shipper")
            etree.SubElement(shipper_node, "Name").text = str(picking_company_id.name)
            if picking_company_id.phone:
                etree.SubElement(shipper_node, "PhoneNumber").text = str(picking_company_id.phone)
            else:
                raise Warning(_("Company phone number is require for sending the request from UPS."))
            etree.SubElement(shipper_node, "AttentionName").text = str(picking_company_id.name)

            etree.SubElement(shipper_node, "ShipperNumber").text = str(self.company_id.ups_shipper_number)
            address = etree.SubElement(shipper_node, "Address")
            if picking_company_id.street:
                etree.SubElement(address, "AddressLine1").text = str(picking_company_id.street)
            else:
                raise Warning(_("AddressLine Is require in company address."))

            etree.SubElement(address, "City").text = "{}".format(picking.company_id and picking.company_id.city)
            etree.SubElement(address, "StateProvinceCode").text = str(picking_company_id.state_id.code or "")
            etree.SubElement(address, "PostalCode").text = str(picking_company_id.zip or "")
            etree.SubElement(address, "CountryCode").text = str(picking_company_id.country_id.code or "")

            to_shipper_node = etree.SubElement(shipment_node, "ShipTo")

            etree.SubElement(to_shipper_node, "CompanyName").text = str(picking_partner_id.name)
            if picking_partner_id.phone:
                etree.SubElement(to_shipper_node, "PhoneNumber").text = str(picking_partner_id.phone)
            else:
                raise Warning(_("Recipient phone number is require."))
            etree.SubElement(to_shipper_node, "AttentionName").text = str(picking_partner_id.name)
            to_address = etree.SubElement(to_shipper_node, "Address")
            if picking_partner_id.street or receiver_street:
                etree.SubElement(to_address, "AddressLine1").text = str(receiver_street)
            else:
                raise Warning(_("AddressLine Is require in customer address."))
            etree.SubElement(to_address, "City").text = str(receiver_city)
            etree.SubElement(to_address, "StateProvinceCode").text = str(receiver_state)
            etree.SubElement(to_address, "PostalCode").text = str(receiver_zip)
            etree.SubElement(to_address, "CountryCode").text = str(receiver_country_code)
            if picking.sale_id and picking.sale_id.ups_shipping_location_id and picking.sale_id.ups_shipping_location_id.location_id:
                etree.SubElement(to_shipper_node, 'LocationID').text = "{}".format(
                    picking.sale_id.ups_shipping_location_id.location_id)
            payment_information = etree.SubElement(shipment_node, "PaymentInformation")
            prepaid_node = etree.SubElement(payment_information, "Prepaid")
            billshipper_node = etree.SubElement(prepaid_node, "BillShipper")
            etree.SubElement(billshipper_node, "AccountNumber").text = str(
                self.company_id and self.company_id.ups_shipper_number)

            service_node = etree.SubElement(shipment_node, "Service")
            etree.SubElement(service_node, "Code").text = str(picking_carrier_id.ups_service_type)
            etree.SubElement(shipment_node, "NumOfPiecesInShipment").text = str(
                len(picking.package_ids) if not total_bulk_weight else (len(picking.package_ids) + 1) or "1")

            for package in picking.package_ids:
                product_weight = self.company_id.weight_convertion(self.ups_weight_uom, package.shipping_weight)
                shipping_box = package.package_type_id or self.ups_default_product_packaging_id
                package_node = etree.SubElement(shipment_node, "Package")
                package_type = etree.SubElement(package_node, "PackagingType")
                etree.SubElement(package_type, "Code").text = "%s" % (
                    self.ups_default_product_packaging_id.shipper_package_code)
                dimension = etree.SubElement(package_node, "Dimensions")
                dimension_uom = etree.SubElement(dimension, "UnitOfMeasurement")
                etree.SubElement(dimension_uom, "Code").text = str("IN" if self.ups_weight_uom != "KGS" else "CM")
                etree.SubElement(dimension, "Length").text = str(shipping_box.packaging_length)
                etree.SubElement(dimension, "Width").text = str(shipping_box.width)
                etree.SubElement(dimension, "Height").text = str(shipping_box.height)
                package_weight = etree.SubElement(package_node, "PackageWeight")
                etree.SubElement(package_weight, "UnitOfMeasurement").text = "%s" % (self.ups_weight_uom)
                etree.SubElement(package_weight, "Weight").text = str(product_weight)
            if total_bulk_weight:
                shipping_box = self.ups_default_product_packaging_id
                package_node = etree.SubElement(shipment_node, "Package")
                package_type = etree.SubElement(package_node, "PackagingType")
                etree.SubElement(package_type, "Code").text = str(
                    self.ups_default_product_packaging_id.shipper_package_code)
                dimension = etree.SubElement(package_node, "Dimensions")
                dimension_uom = etree.SubElement(dimension, "UnitOfMeasurement")
                etree.SubElement(dimension_uom, "Code").text = str("IN" if self.ups_weight_uom != "KGS" else "CM")
                etree.SubElement(dimension, "Length").text = str(shipping_box.packaging_length)
                etree.SubElement(dimension, "Width").text = str(shipping_box.width)
                etree.SubElement(dimension, "Height").text = str(shipping_box.height)
                package_weight = etree.SubElement(package_node, "PackageWeight")
                etree.SubElement(package_weight, "UnitOfMeasurement").text = str(self.ups_weight_uom)
                etree.SubElement(package_weight, "Weight").text = str(total_bulk_weight)

            label_specification = etree.SubElement(shipment_request, "LabelSpecification")
            lable_print_method = etree.SubElement(label_specification, "LabelPrintMethod")
            etree.SubElement(lable_print_method, "Code").text = str(self.ups_lable_print_methods)
            lable_image_formate = etree.SubElement(label_specification, "LabelImageFormat")
            etree.SubElement(lable_image_formate, "Code").text = str(self.ups_lable_print_methods)

            try:
                api.execute('ShipmentConfirmRequest', etree.tostring(shipment_request), version=str(1.0))
                results = api.response.dict()
                _logger.info(results)
            except Exception as e:
                raise Warning(e)

            shippment_digets = results.get('ShipmentConfirmResponse', {}).get('ShipmentDigest', {})
            shippment_accept = {}
            if shippment_digets:
                shippment_accept = self.ups_shipment_accept(shippment_digets)

            # tracking_no=results.get('ShipmentConfirmResponse',{}).get('ShipmentIdentificationNumber',{})
            response_data = shippment_accept.get('ShipmentAcceptResponse', {}) and shippment_accept.get(
                'ShipmentAcceptResponse', {}).get('ShipmentResults', {}) and shippment_accept.get(
                'ShipmentAcceptResponse', {}).get('ShipmentResults', {}).get('PackageResults', {}) or False
            if not response_data:
                raise Warning("ShipmentAccept Request Fail : %s" % (shippment_accept))
            lable_image = shippment_accept.get('ShipmentAcceptResponse', {}).get('ShipmentResults', {}).get(
                'PackageResults', {})
            final_tracking_no = []
            if lable_image:
                if isinstance(lable_image, dict):
                    lable_image = [lable_image]
                for detail in lable_image:
                    tracking_no = detail.get('TrackingNumber')
                    binary_data = detail.get('LabelImage', {}).get('GraphicImage', False)
                    label_binary_data = binascii.a2b_base64(str(binary_data))
                    mesage_ept = (_("Shipment created!<br/> <b>Shipment Tracking Number : </b>%s") % (tracking_no))
                    picking.message_post(body=mesage_ept, attachments=[
                        ('UPS Label-%s.%s' % (tracking_no, self.ups_lable_print_methods), label_binary_data)])
                    final_tracking_no.append(tracking_no)

            shipper_address = picking.picking_type_id.warehouse_id.partner_id
            recipient_address = picking.partner_id
            declared_currency = picking.company_id.currency_id.name
            packages = picking.package_ids

            res = self.ups_get_shipping_rate(shipper_address, recipient_address, total_weight,
                                             picking_bulk_weight=total_bulk_weight, packages=packages,
                                             declared_value=total_value, \
                                             declared_currency=declared_currency)

            # conver currency In Sale order Currency.
            currency_code = res.get('CurrencyCode')
            shipping_charge = res.get('ShippingCharge')
            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            exact_price = rate_currency.compute(float(shipping_charge), picking.sale_id.currency_id)

            # logmessage = (_("Shipment created!<br/> <b>Shipment Tracking Number : </b>%s") % (tracking_no))
            #  picking.message_post(body=logmessage, attachments=[('UPS Label-%s.%s' % (tracking_no, self.ups_lable_print_methods), label_binary_data)])
            if picking.package_ids:
                picking.package_ids.write({'custom_ups_tracking_number': ','.join(final_tracking_no)})
            shipping_data = {
                'exact_price': exact_price,
                'tracking_number': ','.join(final_tracking_no)}
            response += [shipping_data]
        return response
    def ups_shipping_provider_get_tracking_link(self, pickings):
        res = []
        for picking in pickings:
            link = "https://wwwapps.ups.com/WebTracking/track?trackNums="
            res = res + ['%s %s' % (link, picking.carrier_tracking_ref)]
        return res[0]

    def ups_shipping_provider_cancel_shipment(self, picking):
        tracking_no = picking.carrier_tracking_ref.split(',')
        if tracking_no:
            for shipment_number in tracking_no:
                api = self.company_id.get_ups_api_object(self.prod_environment, "Void",
                                                         self.company_id.ups_userid,
                                                         self.company_id.ups_password,
                                                         self.company_id.access_license_number)
                service_root = etree.Element("VoidShipmentRequest")

                request = etree.SubElement(service_root, "Request")
                etree.SubElement(request, "RequestAction").text = "1"
                # shipment_number="1Z12345E0390817264"
                etree.SubElement(service_root, "ShipmentIdentificationNumber").text = str(shipment_number)

                try:
                    api.execute('VoidShipmentRequest', etree.tostring(service_root), version=str(1.0))
                    results = api.response.dict()
                    _logger.info(results)
                except Exception as e:
                    raise ValidationError(e)
        else:
            raise ValidationError(_("Shipment identification number not available!"))
        return True