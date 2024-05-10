import re
import json
import math
import logging
import binascii
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

# We need to validate a ZIP code (U.S. postal code),
# allowing both the five-digit and nine-digit (called ZIP+4) formats.
# The regex should match 12345 and 12345-6789, but not 1234, 123456, 123456789, or 1234-56789.
# https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s14.html#:~:text=You%20need%20to%20validate%20a,123456789%20%2C%20or%201234%2D56789%20.
ZIP_ZIP4_RE = re.compile('^[0-9]{5}(-[0-9]{4})?$')


def validate_zipcode(zipcode):
    if ZIP_ZIP4_RE.match(zipcode) and '-' in zipcode:
        return zipcode.split('-')
    else:
        return [zipcode, '']


def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]), ' '.join(partner_name.split()[-1:])]


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('usps_ts', "USPS")], ondelete={'usps_ts': 'cascade'})
    usps_delivery_type = fields.Selection([('domestic', 'Domestic'),
                                           ('international', 'International')],
                                          string="Delivery Type", default='domestic')

    usps_service_type = fields.Selection([('First Class', 'First Class'),
                                          ('Priority', 'Priority'),
                                          ('Express', 'Express'), ],
                                         required=True, string="Service", default="Priority")

    usps_domestic_container_type = fields.Selection([('VARIABLE', 'VARIABLE / Regular < 12 inch'),
                                                     ('FLAT RATE ENVELOPE', 'FLAT RATE ENVELOPE'),
                                                     ('LEGAL FLAT RATE ENVELOPE', 'LEGAL FLAT RATE ENVELOPE'),
                                                     ('PADDED FLAT RATE ENVELOPE', 'PADDED FLAT RATE ENVELOPE'),
                                                     ('GIFT CARD FLAT RATE ENVELOPE', 'GIFT CARD FLAT RATE ENVELOPE'),
                                                     ('SM FLAT RATE ENVELOPE', 'SM FLAT RATE ENVELOPE'),
                                                     ('WINDOW FLAT RATE ENVELOPE', 'WINDOW FLAT RATE ENVELOPE'),
                                                     ('SM FLAT RATE BOX', 'SM FLAT RATE BOX'),
                                                     ('MD FLAT RATE BOX', 'MD FLAT RATE BOX'),
                                                     ('LG FLAT RATE BOX', 'LG FLAT RATE BOX'),
                                                     ('REGIONALRATEBOXA', 'REGIONALRATEBOXA'),
                                                     ('REGIONALRATEBOXB', 'REGIONALRATEBOXB'),
                                                     ('PACKAGE SERVICE', 'PACKAGE SERVICE'),
                                                     ('CUBIC PARCELS', 'CUBIC PARCELS'),
                                                     ('CUBIC SOFT PACK', 'CUBIC SOFT PACK'), ], default='VARIABLE', string="Container Type")

    usps_intl_container_type = fields.Selection([('VARIABLE', 'VARIABLE / Regular < 12 inch'),
                                                 ('FLATRATEENV', 'FLAT RATE ENVELOPE'),
                                                 ('LEGALFLATRATEENV', 'LEGAL FLAT RATE ENVELOPE'),
                                                 ('PADDEDFLATRATEENV', 'PADDED FLAT RATE ENVELOPE'), ], default='VARIABLE', string="Container Type")

    usps_first_class_mail_type = fields.Selection([('LETTER', 'LETTER'),
                                                   ('FLAT', 'FLAT'),
                                                   ('PACKAGE SERVICE RETAIL', 'PACKAGE SERVICE RETAIL'),
                                                   ('POSTCARD', 'POSTCARD'),
                                                   ('PACKAGE SERVICE', 'PACKAGE SERVICE')],
                                                  string="USPS First Class Mail Type", default="FLAT")

    usps_mail_type = fields.Selection([('ALL', 'All'),
                                       ('PACKAGE', 'PACKAGE'),
                                       ('POSTCARDS', 'POSTCARDS'),
                                       ('ENVELOPE', 'ENVELOPE'),
                                       ('LETTER', 'LETTER'),
                                       ('LARGEENVELOPE', 'LARGE ENVELOPE'),
                                       ('FLATRATE', 'FLAT RATE')],
                                      default="FLATRATE", string="Mail Type")
    usps_content_type = fields.Selection([('MERCHANDISE', 'MERCHANDISE'),
                                          ('SAMPLE', 'SAMPLE'),
                                          ('GIFT', 'GIFT'),
                                          ('DOCUMENTS', 'DOCUMENTS'),
                                          ('RETURN', 'RETURN'),
                                          ('HUMANITARIAN', 'HUMANITARIAN'),
                                          ('DANGEROUSGOODS', 'DANGEROUS GOODS'),
                                          ('CREMATEDREMAINS', 'CREMATED REMAINS')],
                                         default='MERCHANDISE', string="Content Type")

    usps_package_machinable = fields.Boolean(string="Machinable")
    usps_product_packaging_id = fields.Many2one('stock.package.type', string="USPS Package Type")

    usps_label_file_format = fields.Selection([('PDF', 'PDF'), ('TIF', 'TIF')], string="Label Format", default='PDF')
    usps_label_size = fields.Selection([('BARCODE ONLY', 'BARCODE ONLY (Only for Domestic)'),
                                        ('CROP', 'CROP (Only for Domestic)'),
                                        ('4X6LABEL', '4X6LABEL'),
                                        ('4X6LABELL', '4X6LABELL'),
                                        ('4X6LABELP', '4X6LABELP'),
                                        ('4X6LABELP PAGE', '4X6LABELP PAGE (Only for Domestic)'),
                                        ('6X4LABEL', '6X4LABEL (Only for Domestic)'),
                                        ('4X6ZPL203DPI', '4X6ZPL203DPI'),
                                        ('4X6ZPL300DPI', '4X6ZPL300DPI'),
                                        ('SEPARATECONTINUEPAGE', 'SEPARATE CONTINUE PAGE (Only for Domestic)')], string="Label Size", default='4X6LABELL')

    @api.onchange('usps_service_type')
    def on_change_usps_service_type(self):
        if self.usps_service_type != ['FIRST CLASS']:
            self.usps_first_class_mail_type = False

    def _usps_generate_request_type(self, usps_delivery_type, usps_service_type):
        if self.prod_environment:
            request_type = 'eVS' if usps_delivery_type == 'domestic' else "eVS{}{}".format(usps_service_type.replace(' ', ''), 'MailIntl')
        else:
            request_type = 'eVSCertify' if usps_delivery_type == 'domestic' else "eVS{}{}".format(usps_service_type.replace(' ', ''), 'MailIntlCertify')
        return request_type

    def pars_phone_number(self, phone_no):
        # http://diveinto.org/python3/regular-expressions.html
        # 5.6 Case study: Parsing Phone Numbers
        phonePattern = re.compile(r'''
                # don't match beginning of string, number can start anywhere
                (\d{3})     # area code is 3 digits (e.g. '800')
                \D*         # optional separator is any number of non-digits
                (\d{3})     # trunk is 3 digits (e.g. '555')
                \D*         # optional separator
                (\d{4})     # rest of number is 4 digits (e.g. '1212')
                \D*         # optional separator
                (\d*)       # extension is optional and can be any number of digits
                $           # end of string
                ''', re.VERBOSE)
        search = phonePattern.search(phone_no)
        return ''.join(str(number) for number in search.groups()) if search else False

    def usps_ts_prepare_request_data(self, shipper, recipient):
        self.ensure_one()
        request_data = {
            # From Address
            'FromName': shipper.display_name,
            'FromIsCompany': shipper.is_company,
            'FromAddress1': shipper.street or '',
            'FromAddress2': shipper.street2 or '-',
            'FromCity': shipper.city,
            'FromState': shipper.state_id.code or '',
            'FromZip5': validate_zipcode(shipper.zip)[0],
            'FromZip4': validate_zipcode(shipper.zip)[1],
            'FromZip': shipper.zip,
            'FromPhone': self.pars_phone_number(shipper.phone),

            # To Address
            'ToName': recipient.display_name,
            'ToFirstName': _partner_split_name(recipient.name)[0] if _partner_split_name(recipient.name)[0] else _partner_split_name(recipient.name)[1],
            'ToLastName': _partner_split_name(recipient.name)[1] if _partner_split_name(recipient.name)[0] else _partner_split_name(recipient.name)[0],
            'ToIsCompany': recipient.is_company,
            'ToAddress1': recipient.street or '',
            'ToAddress2': recipient.street2 or '-',
            'ToCity': recipient.city,
            'ToState': recipient.state_id.code or '',
            'ToCountry': recipient.country_id.name or '',
            'ToZip5': validate_zipcode(recipient.zip)[0],
            'ToZip4': validate_zipcode(recipient.zip)[1],
            'ToZip': recipient.zip,
            'ToPhone': self.pars_phone_number(recipient.phone),
            'ToPOBoxFlag': 'N',

            'USERID': self.shipping_partner_id.usps_user_id,
            'Revision': '2' if self.usps_delivery_type == 'international' else '',
            'ImageParameters': '',
            'Machinable': self.usps_package_machinable,
            'ImageType': self.usps_label_file_format,
            'ImageLayout': 'ALLINONEFILE',
            'ImageParameter': self.usps_label_size,
            'Agreement': 'Y',
            'NonDeliveryOption': 'ABANDON',
            'ServiceType': self.usps_service_type,
            'ContainerType': self.usps_intl_container_type if self.usps_delivery_type == 'international' else self.usps_domestic_container_type,  # L*W*H required for Rectangular container and L*W*H and Girth required for non-rectagular.
            'ContentType': self.usps_content_type,
            'api_request_type': self._usps_generate_request_type(self.usps_delivery_type, self.usps_service_type),
        }
        return request_data

    def usps_ts_get_package_dimension(self, request_data, package=False):
        if package and package.package_type_id:
            request_data.update({'Length': package.package_type_id.packaging_length, 'Width': package.package_type_id.width, 'Height': package.package_type_id.height, 'Girth': package.package_type_id.girth})
        else:
            request_data.update({'Length': self.usps_product_packaging_id.packaging_length, 'Width': self.usps_product_packaging_id.width, 'Height': self.usps_product_packaging_id.height, 'Girth': self.usps_product_packaging_id.girth})

    def usps_ts_prepare_shipping_content_info(self, picking=False, order=False, package=False):
        customs_items = []
        to_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        from_currency = picking.sale_id.currency_id or picking.company_id.currency_id
        company_id = picking.sale_id.company_id or picking.company_id or self.env.company
        if order:
            for line in order.order_line:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                pounds, ounces = self._usps_ts_convert_weight(line.product_id.weight * line.product_uom_qty)
                customs_items.append({
                    'Description': line.product_id.name,
                    'Quantity': int(line.product_uom_qty) or 1,
                    'Value': from_currency._convert(line.product_id.lst_price * line.product_uom_qty, to_currency, company_id, order.date_order or fields.Date.today()),
                    'NetPounds': pounds,
                    'NetOunces': round(ounces, 0),
                    'CountryOfOrigin': order.warehouse_id.partner_id.country_id.code,
                    'HSTariffNumber': line.product_id.hs_code or '',
                })
            return customs_items
        elif picking and not package:
            for line in picking.move_line_ids:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                pounds, ounces = self._usps_ts_convert_weight(line.product_id.weight * line.qty_done)
                customs_items.append({
                    'Description': line.product_id.name,
                    'Quantity': int(line.qty_done) or 1,
                    'Value': from_currency._convert(line.product_id.lst_price * line.qty_done, to_currency, company_id, picking.sale_id.date_order or fields.Date.today()),
                    'NetPounds': pounds,
                    'NetOunces': round(ounces, 0),
                    'CountryOfOrigin': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                    'HSTariffNumber': line.product_id.hs_code or '',
                })
        elif picking and package:
            for line in picking.move_line_ids.filtered(lambda x: x.result_package_id == package):
                if line.product_id.type not in ['product', 'consu']:
                    continue
                pounds, ounces = self._usps_ts_convert_weight(line.product_id.weight * line.qty_done)
                customs_items.append({
                    'Description': line.product_id.name,
                    'Quantity': int(line.qty_done) or 1,
                    'Value': from_currency._convert(line.product_id.lst_price * line.qty_done, to_currency, company_id, picking.sale_id.date_order or fields.Date.today()),
                    'NetPounds': pounds,
                    'NetOunces': round(ounces, 0),
                    'CountryOfOrigin': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                    'HSTariffNumber': line.product_id.hs_code or '',
                })
        return customs_items

    def usps_ts_send_rate_request(self, order, total_weight, max_weight):
        total_value = sum([(line.price_unit * line.product_uom_qty) for line in order.order_line.filtered(lambda line: not line.is_delivery and not line.display_type)]) or 0.0
        if order.currency_id.name == 'USD':
            value_of_contents = total_value
        else:
            quote_currency = order.currency_id
            currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            value_of_contents = quote_currency._convert(total_value, currency, order.company_id, order.date_order or fields.Date.today())
        try:
            request_data = {
                'USERID': self.shipping_partner_id.usps_user_id,
                'Revision': '2',
                'Package': "{}{}".format('ORDER', order.id),
                'Service': self.usps_service_type,
                'FirstClassMailType': self.usps_first_class_mail_type,
                'MailType': self.usps_mail_type,
                'ValueOfContents': value_of_contents,
                'ZipOrigination': order.warehouse_id.partner_id.zip,
                'ZipDestination': validate_zipcode(order.partner_shipping_id.zip)[0],
                'Country': order.partner_shipping_id.country_id.name,
                'Pounds': total_weight['pounds'],
                'Ounces': total_weight['ounces'],
                'Container': '',
                'Width': self.usps_product_packaging_id.width,
                'Height': self.usps_product_packaging_id.height,
                'Length': self.usps_product_packaging_id.packaging_length,
                'Girth': self.usps_product_packaging_id.girth,
                'Machinable': str(self.usps_package_machinable),
            }

            if order.partner_shipping_id.country_id == order.env.ref('base.ca'):
                # Origin ZIP Code is required to determine
                # Priority Mail International price to Canadian
                # destinations and is used to determine mailability of Global Express Guaranteed. When
                # provided, the response will return a list of Post
                # Office locations where GXG is accepted. The
                # Origin ZIP Code must be valid.
                request_data.update(OriginZip=order.warehouse_id.partner_id.zip)

            if self.usps_delivery_type == 'domestic':
                request_xml = self.env['ir.qweb']._render('usps_delivery.usps_ratev4', request_data)
            else:
                request_xml = self.env['ir.qweb']._render('usps_delivery.usps_intlratev2', request_data)
            api = 'RateV4' if self.usps_delivery_type == 'domestic' else 'IntlRateV2'
            dict_response = self.shipping_partner_id._usps_send_request(params={'API': api, 'XML': request_xml}, prod_environment=self.prod_environment)
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}
        packages = dict_response.get('RateV4Response' if api == 'RateV4' else 'IntlRateV2Response')['Package']
        if isinstance(packages, dict):
            packages = [packages]
        shipping_charge = 0.0
        for package in packages:
            error_dict = package.get('Error')
            if error_dict:
                return {'success': False, 'price': 0.0,
                        'error_message': "[{}] - {}".format(error_dict['Number'], error_dict['Description']),
                        'warning_message': False}
            if api == 'RateV4':
                shipping_charge += float(package['Postage']['Rate'])
            else:
                services = package['Service']
                if isinstance(services, dict):
                    services = [services]
                for service in services:
                    if self.usps_service_type in service.get('SvcDescription'):
                        shipping_charge += float(service.get('Postage'))
        if order.currency_id.name != 'USD':
            rate_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            if rate_currency:
                shipping_charge = rate_currency.compute(shipping_charge, order.currency_id)
        return {'success': True,
                'price': float(shipping_charge),
                'error_message': False,
                'warning_message': False}

    def _usps_ts_convert_weight(self, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        weight_lbs = weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_lb'), round=False)
        pounds = int(math.floor(weight_lbs))
        ounces = round((weight_lbs - pounds) * 16, 3)
        return pounds, ounces

    def usps_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        est_weight_value = sum([(line.product_id.weight * line.product_uom_qty) for line in order.order_line]) or 0.0
        pounds, ounces = self._usps_ts_convert_weight(est_weight_value)
        max_weight = 70  # In pounds
        return self.usps_ts_send_rate_request(order, {'pounds': pounds, 'ounces': ounces}, max_weight=70)

    def usps_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            bulk_pounds, bulk_ounces = self._usps_ts_convert_weight(picking.weight_bulk)
            try:
                # picking.check_packages_are_identical()
                api_request_type = self._usps_generate_request_type(self.usps_delivery_type, self.usps_service_type)
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        pounds, ounces = self._usps_ts_convert_weight(package.shipping_weight)
                        request_data = self.usps_ts_prepare_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                        shipping_contents_list = self.usps_ts_prepare_shipping_content_info(picking=picking, package=package)
                        request_data.update({'ShippingContents': shipping_contents_list, 'GrossPounds': pounds, 'GrossOunces': int(round(ounces, 0)), 'WeightInOunces': 16 * pounds + ounces})
                        self.usps_ts_get_package_dimension(request_data, package=package)
                        request_xml = self.env['ir.qweb']._render('usps_delivery.usps_shipment', request_data)
                        dict_response = self.shipping_partner_id._usps_send_request(params={'API': api_request_type, 'XML': request_xml}, prod_environment=self.prod_environment)
                        error_dict = dict_response.get('Error')
                        if error_dict:
                            raise UserError(_("[{}] - {}".format(error_dict['Number'], error_dict['Description'])))
                        dict_response = dict_response.get('{}Response'.format(api_request_type), {})
                        tracking_number = dict_response.get('BarcodeNumber')
                        label_binary_data = binascii.a2b_base64(dict_response.get('LabelImage'))
                        exact_price += float(dict_response.get('Postage', '0.0'))
                        tracking_number_list.append(tracking_number)
                        attachments.append(('USPS-%s.%s' % (tracking_number, self.usps_label_file_format), label_binary_data))
                # Create one package with the rest (the content that is not in a package)
                if bulk_pounds or bulk_ounces:
                    request_data = self.usps_ts_prepare_request_data(picking.picking_type_id.warehouse_id.partner_id, picking.partner_id)
                    shipping_contents_list = self.usps_ts_prepare_shipping_content_info(picking=picking)
                    request_data.update({'ShippingContents': shipping_contents_list, 'GrossPounds': bulk_pounds, 'GrossOunces': int(round(bulk_ounces, 0)), 'WeightInOunces': 16 * bulk_pounds + bulk_ounces})
                    self.usps_ts_get_package_dimension(request_data)
                    request_xml = self.env['ir.qweb']._render('usps_delivery.usps_shipment', request_data)
                    dict_response = self.shipping_partner_id._usps_send_request(params={'API': api_request_type, 'XML': request_xml}, prod_environment=self.prod_environment)
                    error_dict = dict_response.get('Error')
                    if error_dict:
                        raise UserError(_("[{}] - {}".format(error_dict['Number'], error_dict['Description'])))
                    dict_response = dict_response.get('{}Response'.format(api_request_type), {})
                    tracking_number = dict_response.get('BarcodeNumber')
                    label_binary_data = binascii.a2b_base64(dict_response.get('LabelImage'))
                    exact_price += float(dict_response.get('Postage', '0.0'))
                    tracking_number_list.append(tracking_number)
                    attachments.append(('USPS-%s.%s' % (tracking_number, self.usps_label_file_format), label_binary_data))
                if order.currency_id.name != 'USD':
                    rate_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                    if rate_currency:
                        exact_price = rate_currency._convert(exact_price, order.currency_id, company, order.date_order or fields.Date.today())
                if len(tracking_number_list) == 1:
                    msg = (_("Shipment created into USPS <br/> <b>Tracking Number : </b>%s") % (tracking_number_list[0]))
                else:
                    msg = (_("Shipment created into USPS <br/> <b>Tracking Number : </b>%s") % (",".join(tracking_number_list)))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res = res + [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def usps_ts_get_tracking_link(self, picking):
        tracking_numbers = picking.carrier_tracking_ref.split(',')
        if len(tracking_numbers) == 1:
            return 'https://tools.usps.com/go/TrackConfirmAction_input?qtc_tLabels1=%s' % picking.carrier_tracking_ref
        tracking_urls = []
        for tracking_number in tracking_numbers:
            tracking_urls.append((tracking_number, 'https://tools.usps.com/go/TrackConfirmAction_input?qtc_tLabels1=%s' % tracking_number))
        return json.dumps(tracking_urls)

    # def usps_ts_cancel_shipment(self, picking):
    #     tracking_nos = picking.carrier_tracking_ref.split(',')
    #     if tracking_nos:
    #         api_request_type = 'eVSCancel' if self.prod_environment else 'eVSCancelCertify'
    #         for tracking_no in tracking_nos:
    #             request_data = {'USERID': self.shipping_partner_id.usps_user_id, 'BarcodeNumber': tracking_no, 'usps_delivery_type': self.usps_delivery_type, 'api_request_type': api_request_type}
    #             request_xml = self.env['ir.qweb'].render('usps_delivery.usps_cancel_shipment', request_data)
    #             try:
    #                 dict_response = self.shipping_partner_id._usps_send_request(params={'API': api_request_type, 'XML': request_xml}, prod_environment=self.prod_environment)
    #                 error_dict = dict_response.get('Error')
    #                 if error_dict:
    #                     raise Warning(_("[{}] - {}".format(error_dict['Number'], error_dict['Description'])))
    #             except Exception as e:
    #                 raise Warning(e)
    #     return True
