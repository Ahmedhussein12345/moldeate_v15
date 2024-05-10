import datetime
from email.policy import default
from pyexpat import model
from re import U
from tokenize import String

from odoo import models, fields,api
from odoo.exceptions import UserError
import base64
import requests
import datetime


    



class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    cus_type = fields.Selection([('customer', 'Customer'),
                                      ('prospect', 'Prospect')], string='Type', default='prospect')
    # cus_type_val = fields.Selection([('customer_val', 'Valued Customer'),
    #                                   ('prospect_val', 'Valued Prospect')], string='Contact Type', default='prospect_val',compute="select_type")

    # # @api.onchange('sale_order_count')
    # def select_type(self):
        
    #     for i in self.sale_order_ids:
    #         sale= self.env['sale.order'].search([('id','=',i.id)])
    #         print(sale.id)
    #         for so in sale:
    #             if so.state == 'sale':
    #                 self.cus_type = 'customer'
    #                 break



    #             else:
    #                 self.cus_type = 'prospect'
    
    # def select_type(self):
      
        #         rec.partner_id.cus_type='prospect'
        # for i in self.sale_order_ids:
        #     if self.sale_order_count:
        #         sale= self.env['sale.order'].search([('id','=',i.id)])
        #         print(sale.id)
        #         for so in sale:
        #             if so.state == 'sale':
        #                 self.cus_type_val = 'customer_val'
                        
        #             else:
        #                 self.cus_type_val = 'prospect_val'
        #     else:
        #         self.cus_type_val = 'prospect_val'


        # found=False
        # recs= self.env['sale.order'].search([('partner_id','=',self.id)])
        
     
        # for rec in recs:
            
         
        #     if rec.state=='sale':
        #         found=True
        #         break
        
            
        # if found:
        #     self.cus_type='customer'
        # else:
        #     self.cus_type='prospect'

        
# class InheritSaleOrder(models.Model):
#      _inherit = 'sale.order'

#      @api.onchange('state')
#      def _onchange_state(self):
#         found=False
#         recs= self.env['sale.order'].search([('partner_id','=',self.id)])
        
     
#         for rec in recs:
            
         
#             if rec.state=='sale':
#                 found=True
#                 break
            
        
            
#         if found:
#             rec.cus_type='customer'
#         else:
#             rec.cus_type='prospect'


        
        

