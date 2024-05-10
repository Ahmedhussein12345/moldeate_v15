from odoo import api, fields, models, _, osv
from odoo.exceptions import AccessError, UserError, ValidationError



# class Users(osv.osv):
#     _inherit = 'res.users'
#     _columns = {}

#     def has_group(self,cr,uid,group_ext_id):
#          if '.' in group_ext_id:
#               users_group1 = [x.id for x in self.pool['ir.model.data'].get_object(cr, uid, 'bms',  'xml_id_group1').users]
#               if uid in users_group1:
#                   return super(Users,self).has_group(cr,uid,'ol_inventory_rights.group_restriction_inventory_done_validate')
           
#               else:
#                   return super(Users,self).has_group(cr,uid,'base.group_user')

#          else:
#              return super(Users,self).has_group(cr,uid,group_ext_id)
class StockMoveLineInherit(models.Model):
    _inherit='stock.move.line'

    compute_grp = fields.Boolean('Group Calculate',compute="_compute_group")

    
    def _compute_group(self):
    
        # flag =self.pool.get('res.users').has_group(cr,uid,'ol_inventory_rights.group_restriction_inventory_done_validate'):
        # self.compute_grp = flag

        desired_group_name = self.env['res.groups'].search([('name','=','Inventory Validate')])
        desired_user_gr = self.env.user.id in desired_group_name.users.ids
        self.compute_grp = not(desired_user_gr)
        

