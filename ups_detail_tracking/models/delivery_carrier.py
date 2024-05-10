import logging
import binascii
from odoo.exceptions import UserError
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

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
                    picking.partner_id, picking)
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
                for tracking_num in tracking_number_list:
                    self.env['tracking.number'].create({'name': tracking_num, 'picking_id': picking.id})
                picking.message_post(body=msg, attachments=attachments)
            except Exception as e:
                raise UserError(e)
            res += [{'exact_price': exact_price, 'tracking_number': ",".join(tracking_number_list)}]
        return res
