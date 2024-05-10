from odoo import models, fields, _


class TrackingDetailsUPS(models.Model):
    _name = "tracking.details.ups"
    _description = "Tracking Details UPS"

    tracking_number_id = fields.Many2one('tracking.number', string="Tracking Number")
    picking_id = fields.Many2one('stock.picking', string="Picking")
    city = fields.Char(string="City")
    postal_code = fields.Char(string="Postal Code")
    country_id = fields.Many2one('res.country', string="Country")
    status_type = fields.Selection([
        ('D', 'Delivered'),
        ('I', 'In Transit'),
        ('M', 'Billing Information Received'),
        ('MV', 'Billing Information Voided'),
        ('P', 'Pickup'),
        ('X', 'Exception'),
        ('RS', 'Returned to Shipper'),
        ('DO', 'Delivered Origin CFS (Freight Only)'),
        ('DD', 'Delivered Destination CFS (Freight Only)'),
        ('W', 'Warehousing (Freight Only)'),
        ('NA', 'Not Available'),
        ('O', 'Out for Delivery'),
    ], 'Status Type')
    status_description = fields.Char(string='Description')
    status_code = fields.Char(string="Status Code")
    activity_date = fields.Date(string="Date")
    activity_time = fields.Float(string="Time")
