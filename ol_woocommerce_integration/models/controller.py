from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero
from odoo import http
from odoo.http import request
import subprocess
import sys
import base64
from io import BytesIO
       


class AttachmentController(http.Controller):
    
    @http.route('/my_module/get_attachment/<string:attachment_id>', type='http',website="true", auth='public')
    def get_attachment(self, attachment_id, **get):
        # raise UserError("Shams")
        attachment_id=str(attachment_id).split(".")[0]
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', attachment_id)])
        file_data = base64.b64decode(attachment.datas)
        return request.make_response(file_data, [('Content-Type', attachment.mimetype), ('Content-Disposition', 'attachment; filename="%s"' % str(attachment.name)+"."+str(attachment.mimetype).split('/')[1])])

#         return request.make_response(file_data, [('Content-Type', 'image')])

    

    
