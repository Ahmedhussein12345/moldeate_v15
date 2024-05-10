from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMoveInherit(models.Model):
    _inherit='account.move'

    tracking_number = fields.Text('Tracking Reference', compute="extract_tracking_field")
    

    def extract_tracking_field(self):
        SO=self.env["sale.order"].search([("name",'=',self.invoice_origin)])
        track_nos=""

        count=0
        for res in SO.picking_ids:
            # raise UserError(res.location_id.name)
            if res.location_id.name == "Output":
                count+=1
                if res.carrier_tracking_ref == False:
                    pass
                else:
                    if count>1:
                        track_nos+=","+" "+res.carrier_tracking_ref 
                    else:
                         track_nos+= res.carrier_tracking_ref 
                        
        self.tracking_number= track_nos
        
        
                

        # if 

        
        
        # deliv = self.env["stock.picking"].search([('origin','=',self.invoice_origin)])

        
        # raise UserError(deliv)
        # if "OUT" in SO.
        # delivery = self.SO.search()

