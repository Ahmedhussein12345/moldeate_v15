import json
import datetime
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    tracking_number_id = fields.Many2one('tracking.number', string="Tracking Number")
    tracking_details_ids = fields.Many2many('tracking.details.ups', string="Tracking Details")
    ups_delivery_date = fields.Date(string="Delivery Date", related="tracking_number_id.delivery_date")
    ups_delivery_time = fields.Float(string="Delivery Time", related="tracking_number_id.delivery_time")

    @api.onchange('tracking_number_id')
    def _onchange_display_tracking_details(self):
        if self.tracking_number_id:
            tracking_details_ids = self.env['tracking.details.ups'].search([('tracking_number_id', '=', self.tracking_number_id.id), ('picking_id', '=', self.ids[0])])
            self.write({'tracking_details_ids': [(6, 0, tracking_details_ids.ids)]})
        else:
            self.tracking_details_ids = False

    def refresh_tracking_details(self):
        tracking_details_ups_obj = self.env['tracking.details.ups']
        if self.tracking_number_id:
            headers = {
                'Content-Type': 'application/json',
                'AccessLicenseNumber': '8DA6BF24B4F8D855',
                'Username': self.carrier_id.shipping_partner_id.ups_user_name,
                'Password': self.carrier_id.shipping_partner_id.ups_password,
            }
            api_url = 'https://onlinetools.ups.com/track/v1/details/%s' % self.tracking_number_id.name
            try:
                req = requests.request('GET', api_url, headers=headers)
                req.raise_for_status()
                if isinstance(req.content, bytes):
                    res = req.content.decode("utf-8")
                    response = json.loads(res)
                else:
                    response = json.loads(req.content)
                if response and response.get('trackResponse', False):
                    track_response = response.get('trackResponse').get('shipment', False)
                    for track_res in track_response:
                        if track_res.get('warnings', False):
                            error_message = track_res.get('warnings')
                            raise error_message
                        for res_package in track_res.get('package', False):
                            if res_package.get('deliveryDate', False):
                                delivery_date = datetime.datetime.strptime(res_package['deliveryDate'][0]['date'], '%Y%m%d').date()
                            else:
                                delivery_date = False
                            if res_package.get('deliveryTime', False) and res_package.get('deliveryTime').get('startTime'):
                                delivery_time = datetime.datetime.strptime(res_package['deliveryTime']['startTime'], "%H%M%S").time()
                                delivery_time_split_vals = str(delivery_time).split(':')
                                t, hours = divmod(float(delivery_time_split_vals[0]), 24)
                                t, minutes = divmod(float(delivery_time_split_vals[1]), 60)
                                minutes = minutes / 60.0
                                delivery_time = hours + minutes
                            else:
                                delivery_time = 0.0
                            self.tracking_number_id.write({'delivery_date': delivery_date, 'delivery_time': delivery_time})
                            if res_package.get('activity', False):
                                tracking_activities = res_package.get('activity')
                                for tracking_activity in tracking_activities:
                                    status_type = tracking_activity['status']['type'] or False
                                    status_code = tracking_activity['status']['code'] or False
                                    city = tracking_activity['location']['address']['city'] or False
                                    postal_code = tracking_activity['location']['address']['postalCode'] or False
                                    country_code = tracking_activity['location']['address']['country'] or False
                                    description = tracking_activity['status']['description'] or False
                                    if country_code:
                                        country_id = self.env['res.country'].sudo().search([('code', '=', country_code)], limit=1) or False
                                    else:
                                        country_id = False
                                    activity_date = datetime.datetime.strptime(tracking_activity['date'], '%Y%m%d').date()
                                    activity_time = datetime.datetime.strptime(tracking_activity['time'], "%H%M%S").time()
                                    activity_time_split_vals = str(activity_time).split(':')
                                    t, hours = divmod(float(activity_time_split_vals[0]), 24)
                                    t, minutes = divmod(float(activity_time_split_vals[1]), 60)
                                    minutes = minutes / 60.0
                                    activity_time = hours + minutes
                                    existing_activity = tracking_details_ups_obj.search(
                                        [('tracking_number_id', '=', self.tracking_number_id.id), ('picking_id', '=', self.id), ('status_type', '=', status_type),
                                         ('status_code', '=', status_code),
                                         ('city', '=', city), ('activity_date', '=', activity_date), ('activity_time', '=', activity_time)], limit=1)
                                    if existing_activity:
                                        update_tracking_details_vals = {
                                            'postal_code': postal_code,
                                            'country_id': country_id and country_id.id or country_id,
                                            'status_description': description,
                                            'activity_date': activity_date,
                                            'activity_time': activity_time,
                                        }
                                        existing_activity.write(update_tracking_details_vals)
                                    else:
                                        tracking_details_vals = {
                                            'tracking_number_id': self.tracking_number_id.id,
                                            'picking_id': self.id,
                                            'city': city,
                                            'postal_code': postal_code,
                                            'country_id': country_id and country_id.id or country_id,
                                            'status_type': status_type,
                                            'status_description': description,
                                            'status_code': status_code,
                                            'activity_date': activity_date,
                                            'activity_time': activity_time,
                                        }
                                        tracking_details_ups_obj.create(tracking_details_vals)
            except Exception as e:
                raise UserError("%s" % req.text)
        tracking_details_ids = tracking_details_ups_obj.search([('tracking_number_id', '=', self.tracking_number_id.id), ('picking_id', '=', self.id)])
        self.write({'tracking_details_ids': [(6, 0, tracking_details_ids.ids)]})
        return True
