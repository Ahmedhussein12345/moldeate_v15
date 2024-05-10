from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseInherit(models.Model):
    _inherit='purchase.order'

    qty_count = fields.Integer('Total Quantity', compute="add_quant_sum")

    @api.onchange('order_line')
    def add_quant_sum(self):
        for rec in self:
            sumall=0
            for sl in rec.order_line:
                sumall+=sl.product_uom_qty
            rec["qty_count"]=sumall

    