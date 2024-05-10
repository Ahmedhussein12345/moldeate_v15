# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID


def _post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('ks_curved_backend_theme.ks_color_theme_temp_2').unlink()
    env.ref('ks_curved_backend_theme.ks_color_theme_temp_3').unlink()
    env.ref('ks_curved_backend_theme.ks_color_theme_temp_4').unlink()
    env.ref('ks_curved_backend_theme.ks_color_theme_temp_5').unlink()
    env.ref('ks_curved_backend_theme.ks_color_theme_temp_6').unlink()
