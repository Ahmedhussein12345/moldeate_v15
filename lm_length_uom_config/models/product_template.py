# -*- coding: utf-8 -*-
#################################################################################
# Author      : Leadmaster
# Copyright(c):
# All Rights Reserved.
#################################################################################

import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class LMProductTemplate(models.Model):
    _inherit = "product.template"


    @api.model
    def _get_length_uom_id_from_ir_config_parameter(self):
        res = super(LMProductTemplate, self)._get_length_uom_id_from_ir_config_parameter()
        
        product_length_in_feet_param = self.env['ir.config_parameter'].sudo().get_param('product.volume_in_cubic_feet')
        
        if product_length_in_feet_param == '2':
            return self.env.ref('uom.product_uom_inch')
        
        return res
