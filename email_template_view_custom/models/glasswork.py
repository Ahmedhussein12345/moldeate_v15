
# from odoo import models, fields, api
# from datetime import datetime
# from odoo.exceptions import AccessError, UserError, ValidationError

# class GlassWorkProd(models.Model):
#     _inherit = "product.template"

#     width_prod=fields.Float(string='Width')
#     height_prod=fields.Float(string='Height')
#     size_prod=fields.Char(string='Size', compute='_calculate_size')

#     @api.onchange('width_prod','height_prod')
#     def _calculate_size(self):
#         self.size_prod=''
#         for record in self:
#             if record.width_prod or record.height_prod:
#                 record['size_prod'] = str(record.height_prod).split('.')[0] + ' x ' + str(record.width_prod).split('.')[0]
# class GlassWorkProdProd(models.Model):
#     _inherit = "product.product"

#     width_prod=fields.Float(string='Width')
#     height_prod=fields.Float(string='Height')
#     size_prod=fields.Char(string='Size', compute='_calculate_size')

#     @api.onchange('width_prod','height_prod')
#     def _calculate_size(self):
#         self.size_prod=''
#         for record in self:
#             if record.width_prod or record.height_prod:
#                 record['size_prod'] = str(record.height_prod).split('.')[0] + ' x ' + str(record.width_prod).split('.')[0]

# class GlassWork(models.Model):
#     _inherit = "sale.order.line"
   

#     service_product_ids = fields.Many2many(
#     'product.product', string='Service Products',
#     domain="[('detailed_type', '=', 'service')]",
#     help="Quality Point will apply to every selected Products.")

#     product_parent_ref_id=fields.Many2one(
#     'sale.order.line', string='Parent id')

#     child_ref_ids=fields.One2many(
#     'sale.order.line',"product_parent_ref_id", string='Child ids')

#     product_type=fields.Selection( [("service", "Service"),
#         ("product", "Storable"),
#         ("consu", "Consumbale")],related="product_id.detailed_type")

#     width_prod_line=fields.Float(string='Width')
#     height_prod_line=fields.Float(string='Height')
#     sqm_prod_line=fields.Float(string='SQM',compute='calculate_sqm')

  

#     @api.onchange('product_id')
    
#     def _onchange_product_id(self):
#         for line in self:
#             if line.product_id.detailed_type=='product':

#                 line.width_prod_line=line.product_id.width_prod
#                 line.height_prod_line=line.product_id.height_prod
#                 for child in line.child_ref_ids:
#                     child.width_prod_line=line.product_id.width_prod
#                     child.height_prod_line=line.product_id.height_prod






#     @api.onchange('width_prod_line','height_prod_line','product_uom')
#     def calculate_sqm(self):
#         self.sqm_prod_line=0.0
#         for record in self:
#             if record.product_id.uom_id.id != 7:
#                 if record.width_prod_line or record.height_prod_line:
#                     record['sqm_prod_line'] = (record.width_prod_line * record.height_prod_line)/1000000
#                     record['product_uom_qty'] = record.sqm_prod_line
      
#             elif record.product_id.uom_id.id == 7:
#                 if record.width_prod_line or record.height_prod_line:
#                     _width = (record.width_prod_line + record.width_prod_line)
#                     _height = (record.height_prod_line + record.height_prod_line)
#                     _long = _width + _height
#                     record['sqm_prod_line'] = _long /1000

#     def trigger_prod(self):
    
#         # sale_ord=self.env['sale.order'].search([('order_line', '=', self.id)])
#         # sale_ord._onchange_categ()
#         for line in self:
#             if line.product_id.detailed_type=='product':
#                     for service_prod in line.service_product_ids:
#                         found=False
#                         for child_id in line.child_ref_ids:
#                             if service_prod.id==child_id.product_id.id:
#                                 found=True
#                                 break
#                         if found:
#                             continue
#                         line_item = {

#                                     'product_id':service_prod.id,
#                                     'name': service_prod.name,
#                                     'product_uom_qty': 1,
#                                     'product_uom' : service_prod.uom_id.id,
#                                     'order_id': self.id,
#                                     'product_parent_ref_id':line.id,
#                                     'order_id':line.order_id.id,
                                    
                                                                
#                                 }
            
#                         createdline=self.env['sale.order.line'].create(line_item)
#                         createdline.width_prod_line=line.width_prod_line
#                         createdline.height_prod_line=line.height_prod_line
                            
#                     for child_id in line.child_ref_ids:
#                         found=False
#                         for service_prod in line.service_product_ids:
#                             if service_prod.id==child_id.product_id.id:
#                                 found=True
#                                 break
#                         if not found:
#                             child_id.unlink()
#             line.order_id.prod_sequence()

                        

                


# class GlassWorkOrder(models.Model):
#     _inherit = "sale.order"

#     @api.onchange('order_line')
#     def prod_sequence(self):
#         for order in self:
#             sequence=1
#             other_lines=order.order_line
#             parent_lines=order.env['sale.order.line'].search([('order_id',"=",order.id),('child_ref_ids','!=',False)])
#             for p in parent_lines:
#                 p.sequence=sequence
#                 other_lines-=p
#                 sequence+=1
#                 for c in p.child_ref_ids:
#                     c.sequence=sequence
#                     sequence+=1
#                     other_lines-=c
#             for o in other_lines:
#                 o.sequence=sequence
#                 sequence+=1
    

# class GlassWorktask(models.Model):
#     _inherit = "project.task"

#     # product_service=fields.Char(related='sale_line_id.product_parent_ref_id.name')
#     width_proj_line=fields.Float(string='Width',related='sale_line_id.product_parent_ref_id.width_prod_line')
#     height_proj_line=fields.Float(string='Height',related='sale_line_id.product_parent_ref_id.height_prod_line')
#     # sqm_proj_line=fields.Float(string='SQM',related='sale_line_id.product_parent_ref_id.sqm_prod_line')




        