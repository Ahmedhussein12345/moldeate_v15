# Copyright 2018-2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
# from odoo.http import request, content_disposition, Response
# from odoo.http import ALLOWED_DEBUG_MODES
# from odoo.tools.misc import str2bool
#
#
# class IrHttp(models.AbstractModel):
#     _inherit = 'ir.http'
#
#     @classmethod
#     def _handle_debug(cls):
#         if 'debugg' in request.httprequest.args:
#             debug_mode = []
#             for debug in request.httprequest.args['debugg'].split(','):
#                 if debug not in ALLOWED_DEBUG_MODES:
#                     debug = '1' if str2bool(debug, debug) else ''
#                 debug_mode.append(debug)
#             debug_mode = ','.join(debug_mode)
#             # Write on session only when needed
#             if debug_mode != request.session.debug:
#                 request.session.debug = debug_mode
#         else:
#             request.session.debug = ''



class ResUsers(models.Model):
    _inherit = "res.users"

    chatter_position = fields.Selection(
        [("normal", "Normal"), ("sided", "Sided")],
        default="normal",
    )

    """Override to add access rights.
    Access rights are disabled by default, but allowed on some specific
    fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
    """

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["chatter_position"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["chatter_position"]
