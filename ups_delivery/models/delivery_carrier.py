import logging
import binascii
import base64
import io
from PIL import Image
import PIL.PdfImagePlugin
from odoo.exceptions import UserError
from odoo import models, fields, api, tools, _
from datetime import datetime
import re

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("ups_ts", "UPS")], ondelete={'ups_ts': 'cascade'})
    ups_service_type = fields.Selection([
        ('03', 'UPS Ground'),
        ('11', 'UPS Standard'),
        ('01', 'UPS Next Day'),
        ('14', 'UPS Next Day AM'),
        ('13', 'UPS Next Day Air Saver'),
        ('02', 'UPS 2nd Day'),
        ('59', 'UPS 2nd Day AM'),
        ('12', 'UPS 3-day Select'),
        ('65', 'UPS Saver'),
        ('07', 'UPS Worldwide Express'),
        ('08', 'UPS Worldwide Expedited'),
        ('54', 'UPS Worldwide Express Plus'),
        ('96', 'UPS Worldwide Express Freight')
    ], string="Service Type")

    ups_package_weight_uom = fields.Selection([
        ('LBS', 'Pounds'),
        ('KGS', 'Kilograms')], string="Weight UoM", default='LBS')

    ups_package_dimension_unit_ts = fields.Selection([
        ('IN', 'Inches'), ('CM', 'Centimeters')],
        string="Package size(Units)", default='IN')

    ups_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    ups_label_file_type = fields.Selection([
        ('GIF', 'PDF'),
        ('ZPL', 'ZPL'),
        ('EPL', 'EPLsss'),
        ('SPL', 'SPL')], string="Label File Type", default="GIF")
    ups_international_form_type = fields.Selection([('01', 'Invoice')], string="International Form")
    ups_terms_of_shipments = fields.Selection([('CFR', 'Cost and Freight'),
                                               ('CIF', 'Cost Insurance and Freight'),
                                               ('CIP', 'Carriage and Insurance Paid'),
                                               ('CPT', 'Carriage Paid To'),
                                               ('DAF', 'Delivered at Frontier'),
                                               ('DDP', 'Delivery Duty Paid'),
                                               ('DDU', 'Delivery Duty Unpaid'),
                                               ('DEQ', 'Delivered Ex Quay'),
                                               ('DES', 'Delivered Ex Ship'),
                                               ('EXW', 'Ex Works'),
                                               ('FAS', 'Free Alongside Ship'),
                                               ('FCA', 'Free Carrier'),
                                               ('FOB', 'Free On Board'), ], string="Terms of Shipments")

    # ups_cn_22_size = fields.Selection([('6', '4x6'), ('1', '8.5x11')], string="CN22 Size")
    # ups_cn_22_file_type = fields.Selection([('pdf','PDF'), ('png','PNG'), ('gif','GIF'), ('zpl','ZPL'), ('star','Star'), ('epl2','EPL2'), ('spl','SPL')], string="CN 22 File Type")

    def ups_ts_prepare_request_data_for_rate_request(self, shipper, recipient):
        self.ensure_one()
        shipping_partner_id = self.shipping_partner_id
        request_data = {'RateRequest':
                            {'Shipment':
                                 {'ShipmentRatingOptions': {'NegotiatedRatesIndicator': "TRUE"},
                                  'Service': {'Code': self.ups_service_type,
                                              'Description': self.name},
                                  'Shipper': {'Name': shipper.name,
                                              'ShipperNumber': shipping_partner_id.ups_shipper_number,
                                              'Address': {'AddressLine': shipper.street,
                                                          'City': shipper.city,
                                                          'StateProvinceCode': shipper.state_id.code,
                                                          'PostalCode': shipper.zip,
                                                          'CountryCode': shipper.country_id.code,
                                                          }
                                              },
                                  'ShipTo': {'Name': recipient.name,
                                             'Address': {'AddressLine': recipient.street,
                                                         'City': recipient.city,
                                                         'StateProvinceCode': recipient.state_id.code,
                                                         'PostalCode': recipient.zip,
                                                         'CountryCode': recipient.country_id.code,
                                                         }
                                             },
                                  'ShipFrom':
                                      {'Name': shipper.name,
                                       'Address': {'AddressLine': shipper.street,
                                                   'City': shipper.city,
                                                   'StateProvinceCode': shipper.state_id.code,
                                                   'PostalCode': shipper.zip,
                                                   'CountryCode': shipper.country_id.code,
                                                   }
                                       },
                                  }}}
        return request_data

    def ups_ts_prepare_request_data_for_shipment_request(self, shipper, recipient, picking, order=False):
        self.ensure_one()
        shipping_partner_id = self.shipping_partner_id
        monetary_value = 0.0
        for move_line in picking.move_line_ids:
            if move_line.move_id.sale_line_id:
                unit_price = move_line.move_id.sale_line_id.price_reduce_taxinc
                qty = move_line.product_uom_id._compute_quantity(move_line.move_id.sale_line_id.product_qty, move_line.move_id.sale_line_id.product_uom)
            else:
                unit_price = move_line.product_id.list_price
                qty = move_line.product_uom_id._compute_quantity(move_line.qty_done, move_line.product_id.uom_id)
            monetary_value += unit_price * qty
        shipper_number = re.sub('[^a-zA-Z0-9]+', '', shipper.phone or shipper.mobile)
        recipient_number = re.sub('[^a-zA-Z0-9]+', '', recipient.phone or recipient.mobile)
        request_data = {'ShipmentRequest':
                            {'Shipment':
                                 {'ShipmentRatingOptions': {'NegotiatedRatesIndicator': "TRUE"},
                                  'Description': picking.origin or picking.name,
                                  'InvoiceLineTotal': {'MonetaryValue': str(monetary_value),
                                                       'CurrencyCode': self.env.company.currency_id.name},
                                  'Service': {'Code': self.ups_service_type,
                                              'Description': self.name},
                                  'Shipper': {'Name': shipper.name,
                                              'AttentionName': shipper.name,
                                              'ShipperNumber': shipping_partner_id.ups_shipper_number,
                                              'Phone': {'Number': shipper_number},
                                              'Address': {'AddressLine': shipper.street,
                                                          'City': shipper.city,
                                                          'StateProvinceCode': shipper.state_id.code,
                                                          'PostalCode': shipper.zip,
                                                          'CountryCode': shipper.country_id.code,
                                                          }
                                              },
                                  'ShipTo': {'Name': recipient.name,
                                             'AttentionName': recipient.name,
                                             'Phone': {'Number': recipient_number},
                                             'Address': {'AddressLine': recipient.street,
                                                         'City': recipient.city,
                                                         'StateProvinceCode': recipient.state_id.code,
                                                         'PostalCode': recipient.zip,
                                                         'CountryCode': recipient.country_id.code,
                                                         }
                                             },
                                  'ShipFrom':
                                      {'Name': shipper.name,
                                       'AttentionName': shipper.name,
                                       'Phone': {'Number': shipper_number},
                                       'Address': {'AddressLine': shipper.street,
                                                   'City': shipper.city,
                                                   'StateProvinceCode': shipper.state_id.code,
                                                   'PostalCode': shipper.zip,
                                                   'CountryCode': shipper.country_id.code,
                                                   }
                                       },
                                  'PaymentInformation': {'ShipmentCharge': {
                                      'Type': '01',
                                      'BillShipper': {"AccountNumber": shipping_partner_id.ups_shipper_number}}
                                  },
                                  }}}
        if self.ups_international_form_type == '01':
            products = []
            invoices = self.env['account.move']
            recipient_number = re.sub('[^a-zA-Z0-9]+', '', recipient.phone or recipient.mobile)
            for line in picking.move_line_ids:
                if line.product_id.type not in ['product', 'consu']:
                    continue
                if not line.move_id.sale_line_id.invoice_lines.mapped('move_id'):
                    raise UserError(_("Invoice number needed to process international shipment. Invoice not found for product : %s." % line.product_id.name))
                invoices |= line.move_id.sale_line_id.invoice_lines.mapped('move_id')
                price = line.move_id.sale_line_id and line.move_id.sale_line_id.price_unit or line.product_id.list_price or line.product_id.price_extra
                products.append({
                    'Description': line.product_id.name,
                    'Unit': {'Number': str(int(line.qty_done)), 'UnitOfMeasurement': {'Code': 'LBS', 'Description': 'Piece'},
                             'Value': str(tools.float_round(price * line.qty_done, precision_digits=2))},
                    'CommodityCode': line.product_id.hs_code or '',
                    'PartNumber': line.product_id.default_code,
                    'OriginCountryCode': picking.picking_type_id.warehouse_id.partner_id.country_id.code,
                })
            request_data['ShipmentRequest']['Shipment']['ShipmentServiceOptions'] = {
                'InternationalForms': {
                    'FormType': self.ups_international_form_type,
                    'Product': products,
                    'InvoiceNumber': invoices[0].name,
                    'PurchaseOrderNumber': picking.origin or picking.sale_id.name,
                    'InvoiceDate': datetime.strftime(invoices[0].invoice_date, "%Y%m%d"),
                    'TermsOfShipment': self.ups_terms_of_shipments,
                    'ReasonForExport': 'SALE',
                    # A reason to export the current international shipment. Valid values: SALE, GIFT, SAMPLE, RETURN, REPAIR, INTERCOMPANYDATA, Any other reason.
                    'Comments': '',
                    'DeclarationStatement': '',
                    'CurrencyCode': invoices[0].currency_id.name,
                    'Contacts': {'SoldTo': {'Name': recipient.name,
                                            'AttentionName': recipient.name,
                                            'Phone': {'Number': recipient_number},
                                            'Address': {'AddressLine': recipient.street,
                                                        'City': recipient.city,
                                                        'StateProvinceCode': recipient.state_id.code,
                                                        'PostalCode': recipient.zip,
                                                        'CountryCode': recipient.country_id.code,
                                                        }
                                            },
                                 }
                }
            }
        return request_data

    def _ups_ts_convert_weight(self, unit, weight):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if unit == 'KGS':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_kgm'), round=False)
        elif unit == 'LBS':
            return weight_uom_id._compute_quantity(weight, self.env.ref('uom.product_uom_lb'), round=False)
        else:
            raise ValueError

    def _ups_ts_convert_dimensions(self, unit, length, width, height):
        length_uom_id = self.env['product.template']._get_length_uom_id_from_ir_config_parameter()
        if unit == 'IN':
            package_legth = length_uom_id._compute_quantity(length, self.env.ref('uom.product_uom_inch'), round=False)
            package_width = length_uom_id._compute_quantity(width, self.env.ref('uom.product_uom_inch'), round=False)
            package_height = length_uom_id._compute_quantity(height, self.env.ref('uom.product_uom_inch'), round=False)
            return package_legth, package_width, package_height
        elif unit == 'CM':
            package_legth = length_uom_id._compute_quantity(length, self.env.ref('uom.product_uom_cm'), round=False)
            package_width = length_uom_id._compute_quantity(width, self.env.ref('uom.product_uom_cm'), round=False)
            package_height = length_uom_id._compute_quantity(height, self.env.ref('uom.product_uom_cm'), round=False)
            return package_legth, package_width, package_height
        else:
            raise ValueError

    def ups_ts_send_rate_request(self, order, total_weight, max_weight):
        total_cost = 0.0
        try:
            request_data = self.ups_ts_prepare_request_data_for_rate_request(order.warehouse_id.partner_id,
                                                                             order.partner_shipping_id)
            for line in order.order_line.filtered(lambda line: not line.is_delivery and not line.display_type):
                total_cost += order.company_id.currency_id._convert(line.product_qty * line.product_id.standard_price, line.product_id.currency_id, order.company_id, fields.Date.today())
            package_list = []
            if max_weight and total_weight > max_weight:
                total_package = int(total_weight / max_weight)
                last_package_weight = total_weight % max_weight

                for index in range(total_package):
                    package_list.append({
                        "PackagingType": {
                            "Code": self.ups_product_packaging_id.shipper_package_code,
                            "Description": self.ups_product_packaging_id.name
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_dimension_unit_ts
                            },
                            "Length": str(self.ups_product_packaging_id.packaging_length),
                            "Width": str(self.ups_product_packaging_id.width),
                            "Height": str(self.ups_product_packaging_id.height)
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_weight_uom,
                            },
                            "Weight": str(max_weight)
                        },
                        "PackageServiceOptions": {
                            "DeclaredValue": {
                                "CurrencyCode": order.currency_id.name,
                                "MonetaryValue": total_cost / total_package,
                            },
                        }
                    })
                if last_package_weight:
                    package_list.append({
                        "PackagingType": {
                            "Code": self.ups_product_packaging_id.shipper_package_code,
                            "Description": self.ups_product_packaging_id.name
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_dimension_unit_ts
                            },
                            "Length": str(self.ups_product_packaging_id.packaging_length),
                            "Width": str(self.ups_product_packaging_id.width),
                            "Height": str(self.ups_product_packaging_id.height),
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_weight_uom,
                            },
                            "Weight": str(last_package_weight)
                        },
                        "PackageServiceOptions": {
                            "DeclaredValue": {
                                "CurrencyCode": order.currency_id.name,
                                "MonetaryValue": total_cost / (total_package + 1),
                            },
                        }
                    })
            else:
                package_list.append({
                    "PackagingType": {
                        "Code": self.ups_product_packaging_id.shipper_package_code,
                        "Description": self.ups_product_packaging_id.name
                    },
                    "Dimensions": {
                        "UnitOfMeasurement": {
                            "Code": self.ups_package_dimension_unit_ts
                        },
                        "Length": str(self.ups_product_packaging_id.packaging_length),
                        "Width": str(self.ups_product_packaging_id.width),
                        "Height": str(self.ups_product_packaging_id.height)
                    },
                    "PackageWeight": {
                        "UnitOfMeasurement": {
                            "Code": self.ups_package_weight_uom,
                        },
                        "Weight": str(total_weight)
                    },
                    "PackageServiceOptions": {
                        "DeclaredValue": {
                            "CurrencyCode": order.currency_id.name,
                            "MonetaryValue": total_cost,
                        },
                    }
                })
            shipment_total_weight_dict = {
                "UnitOfMeasurement": {
                    "Code": self.ups_package_weight_uom,
                    "Description": ""
                },
                "Weight": str(total_weight)
            }
            request_data['RateRequest']['Shipment'].update(
                {'Package': package_list, 'ShipmentTotalWeight': shipment_total_weight_dict})
            response = self.shipping_partner_id._ups_send_request('/rating/Rate', request_data, self.prod_environment,
                                                                  method="POST")
        except Exception as e:
            return {'success': False, 'price': 0.0, 'error_message': e, 'warning_message': False}
        rated_shipment = response.get('RateResponse', {}).get('RatedShipment', {})
        if 'NegotiatedRateCharges' in rated_shipment:
            shipping_charge, shipping_currency = rated_shipment.get('NegotiatedRateCharges', {}).get('TotalCharge', {}).get('MonetaryValue', False), rated_shipment.get(
                'NegotiatedRateCharges', {}).get('TotalCharge', {}).get('CurrencyCode', False)
        else:
            shipping_charge, shipping_currency = rated_shipment.get('TotalCharges', {}).get('MonetaryValue', False), rated_shipment.get('TotalCharges', {}).get('CurrencyCode', False)
        if order.currency_id.name != shipping_currency:
            rate_currency = self.env['res.currency'].search([('name', '=', shipping_currency)], limit=1)
            if rate_currency:
                shipping_charge = rate_currency.compute(float(shipping_charge), order.currency_id)
        return {'success': True,
                'price': float(shipping_charge),
                'error_message': False,
                'warning_message': False}

    def ups_ts_rate_shipment(self, order):
        check_value = self.check_required_value_shipping_request(order)
        if check_value:
            return {'success': False, 'price': 0.0, 'error_message': check_value, 'warning_message': False}
        est_weight_value = sum(
            [(line.product_id.weight * line.product_uom_qty) for line in order.order_line.filtered(
                lambda x: not x.product_id.type in ['service', 'digital'])]) or 0.0
        total_weight = self._ups_ts_convert_weight(self.ups_package_weight_uom, est_weight_value)
        max_weight = self._ups_ts_convert_weight(self.ups_package_weight_uom, self.ups_product_packaging_id.max_weight)
        return self.ups_ts_send_rate_request(order, total_weight, max_weight)

    def ups_ts_convert_label_to_pdf(self, GraphicImage):
        decoded_bytes = base64.decodebytes(GraphicImage.encode('utf-8'))
        if self.ups_label_file_type == 'GIF':
            decoded_string = io.BytesIO(decoded_bytes)
            im = Image.open(decoded_string)
            # im = im.rotate(45)
            label_result = io.BytesIO()
            im.save(label_result, 'pdf')
            return label_result.getvalue()
        else:
            return decoded_bytes

    @api.model
    def ups_ts_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            exact_price = 0.0
            tracking_number_list = []
            attachments = []
            order = picking.sale_id
            company = order.company_id or picking.company_id or self.env.user.company_id
            order_currency = picking.sale_id.currency_id or picking.company_id.currency_id
            total_bulk_weight = self._ups_ts_convert_weight(self.ups_package_weight_uom, picking.weight_bulk)
            try:
                request_data = self.ups_ts_prepare_request_data_for_shipment_request(
                    picking.picking_type_id.warehouse_id.partner_id,
                    picking.partner_id,picking)
                packages = []
                package_names = []
                if picking.package_ids:
                    # Create all packages
                    for package in picking.package_ids:
                        package_total_cost = 0.0
                        package_weight = self._ups_ts_convert_weight(self.ups_package_weight_uom,
                                                                     package.shipping_weight)
                        package_legth, package_width, package_height = self._ups_ts_convert_dimensions(self.ups_package_dimension_unit_ts,
                                                                                                       package.package_type_id.packaging_length, package.package_type_id.width,
                                                                                                       package.package_type_id.height)
                        for quant in package.quant_ids:
                            package_total_cost += company.currency_id._convert(quant.quantity * quant.product_id.standard_price, quant.product_id.currency_id, picking.company_id,
                                                                               fields.Date.today())
                        packages.append({
                            "Description": package.package_type_id.name,
                            "Packaging": {
                                "Code": package.package_type_id.shipper_package_code,
                            },
                            "Dimensions": {
                                "UnitOfMeasurement": {
                                    "Code": self.ups_package_dimension_unit_ts
                                },
                                "Length": str(package_legth),
                                "Width": str(package_width),
                                "Height": str(package_height)
                            },
                            "PackageWeight": {
                                "UnitOfMeasurement": {
                                    "Code": self.ups_package_weight_uom,
                                },
                                "Weight": str(package_weight)
                            },
                            "PackageServiceOptions": {
                                "DeclaredValue": {
                                    "CurrencyCode": picking.company_id.currency_id.name,
                                    "MonetaryValue": package_total_cost,
                                    "Type": {
                                        "Code": '01'  # EVS
                                    },
                                },
                            }
                        })
                        package_names.append(package.name)
                # Create one package with the rest (the content that is not in a package)
                if total_bulk_weight:
                    package_total_cost = 0.0
                    for move_line in picking.move_line_ids:
                        package_total_cost += company.currency_id._convert(move_line.qty_done * move_line.product_id.standard_price, move_line.product_id.currency_id, picking.company_id,
                                                                           fields.Date.today())
                    packages.append({
                        "Description": self.ups_product_packaging_id.name,
                        "Packaging": {
                            "Code": self.ups_product_packaging_id.shipper_package_code,
                        },
                        "Dimensions": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_dimension_unit_ts
                            },
                            "Length": str(self.ups_product_packaging_id.packaging_length),
                            "Width": str(self.ups_product_packaging_id.width),
                            "Height": str(self.ups_product_packaging_id.height)
                        },
                        "PackageWeight": {
                            "UnitOfMeasurement": {
                                "Code": self.ups_package_weight_uom,
                            },
                            "Weight": str(total_bulk_weight),
                        },
                        "PackageServiceOptions": {
                            "DeclaredValue": {
                                "CurrencyCode": picking.company_id.currency_id.name,
                                "MonetaryValue": package_total_cost,
                                "Type": {
                                    "Code": '01'  # EVS
                                },
                            },
                        }
                    })
                request_data['ShipmentRequest']['Shipment'].update({'Package': packages})
                request_data['ShipmentRequest'].update({'LabelSpecification': {'LabelImageFormat': {'Code': self.ups_label_file_type, 'Description': self.ups_label_file_type}}})
                if self.ups_label_file_type != 'GIF':
                    request_data['ShipmentRequest']['LabelSpecification'].update({'LabelStockSize': {'Height': '6', 'Width': '4'}})
                request_data['ShipmentRequest']['Shipment'].update({'Package': packages, 'LabelSpecification': {
                    'LabelImageFormat': {'code': self.ups_label_file_type}}})
                response = self.shipping_partner_id._ups_send_request('/shipments?additionaladdressvalidation=city',
                                                                      request_data, self.prod_environment,
                                                                      method="POST")
                shipment_results = response.get('ShipmentResponse', {}).get('ShipmentResults', {})
                package_results = shipment_results.get('PackageResults')
                shipment_charge_results = shipment_results.get('ShipmentCharges')
                if package_results:
                    if isinstance(package_results, dict):
                        package_results = [package_results]
                    for package in package_results:
                        tracking_number = package.get('TrackingNumber')
                        label_binary_data = self.ups_ts_convert_label_to_pdf(package.get('ShippingLabel', {}).get('GraphicImage', False))
                        # label_binary_data = binascii.a2b_base64(str(binary_data))
                        tracking_number_list.append(tracking_number)
                        attachments.append(
                            ('UPS-%s.%s' % (tracking_number, 'PDF' if self.ups_label_file_type == 'GIF' else self.ups_label_file_type), label_binary_data))
                    if shipment_charge_results.get('TotalCharges', {}).get('CurrencyCode') == order_currency.name:
                        exact_price += float(shipment_charge_results.get('TotalCharges', {}).get('MonetaryValue'))
                    else:
                        company_currency = picking.company_id.currency_id
                        float_charge = float(shipment_charge_results.get('TotalCharges', {}).get('MonetaryValue'))
                        exact_price += company_currency._convert(float_charge, order_currency, company, order.date_order or fields.Date.today())
                if shipment_results.get('Form', {}) and shipment_results.get('Form').get('Code') == self.ups_international_form_type:
                    form_binary_data = binascii.a2b_base64(str(shipment_results['Form']['Image']['GraphicImage']))
                    attachments.append(("CA-%s.pdf" % picking.name, form_binary_data))
                if len(tracking_number_list) == 1:
                    msg = (_("Shipment created into UPS <br/> <b>Tracking Number : </b>%s") % (tracking_number_list[0]))
                else:
                    msg = (_("Shipment created into UPS <br/> <b>Tracking Number : </b>%s") % (",".join(tracking_number_list)))
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res += [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res

    def ups_ts_get_tracking_link(self, picking):
        return 'http://wwwapps.ups.com/WebTracking/track?track=yes&trackNums=%s' % picking.carrier_tracking_ref

    def ups_ts_cancel_shipment(self, picking):
        tracking_nos = picking.carrier_tracking_ref.split(',')
        if tracking_nos:
            for tracking_no in tracking_nos:
                try:
                    response = self.shipping_partner_id._ups_send_request('/shipments/cancel/%s' % tracking_no, {}, self.prod_environment, method="DELETE")
                except Exception as e:
                    raise UserError(e)
        return True
