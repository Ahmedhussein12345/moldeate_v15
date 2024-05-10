from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseInherit(models.Model):
    _inherit='stock.picking'

    qty_count = fields.Integer('Quantity Count', compute="add_quant_sum")

    @api.onchange('move_ids_without_package')
    def add_quant_sum(self):
        for rec in self:
            sumall=0
            for sl in rec.move_ids_without_package:
                sumall+=sl.product_uom_qty
            rec["qty_count"]=sumall

    