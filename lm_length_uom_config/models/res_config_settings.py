# -*- coding: utf-8 -*-
#################################################################################
# Author      : Leadmaster
# Copyright(c):
# All Rights Reserved.
#################################################################################

import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class LMResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    product_volume_volume_in_cubic_feet = fields.Selection([
        ('0', 'Meters'),
        ('1', 'Feet'),
        ('2','Inch'),
    ], 'length unit of measure', config_parameter='product.volume_in_cubic_feet', default='0')
