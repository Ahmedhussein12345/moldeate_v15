from odoo import api, fields, models, _, osv
from odoo.exceptions import AccessError, UserError, ValidationError




class StockMoveLineInherit(models.Model):
    _inherit='stock.move.line'


    @api.onchange('qty_done')
    def productqty_and_demand_check(self):

        if self.env['res.users'].has_group(str('ol_inventory_rights.group_user')) :
            for line in self: 
                    if line.product_id.qty_available < line.qty_done: 
                        raise UserError(str("Not Enough Quantity in Stock"))
        else:
            pass





        

        
