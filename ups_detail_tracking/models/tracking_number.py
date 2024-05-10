from odoo import models, fields


class TrackingNumber(models.Model):
    _name = "tracking.number"
    _description = "Tracking Number"

    name = fields.Char(string="Tracking Number", required="1")
    picking_id = fields.Many2one('stock.picking', string="Picking", required="1")
    delivery_date = fields.Date(string="Delivery Date")
    delivery_time = fields.Float(string="Delivery Time")
