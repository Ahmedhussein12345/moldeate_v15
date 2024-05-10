from odoo import models, fields
#from woocommerce import API
from odoo.exceptions import UserError

class ProductsWooLogs(models.Model):
    _name = 'woocommerce.orders.status.logs'
    odoo_id = fields.Many2one("sale.order","Odoo Order ID")
    woo_id = fields.Integer("Woocommerce Order ID")
    status_select = [
        ('complete', 'Completed'),
        ('error', 'Error'),
    ]
    status = fields.Selection(selection=status_select,string='Status')
    
    details = fields.Char("Details")
    main_id = fields.Many2one(comodel_name='woocommerce.main',relation='order_status_odoo_to_woo_log_ids', string="Order Status Logs")


