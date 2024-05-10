# -*- encoding: utf-8 -*-
import werkzeug

from odoo import http
from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)
   

class HSPHome(Home, http.Controller):

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        ensure_db()
        _logger.info("kw >>>>>>>>>{}".format(kw))
        _logger.info("s_action >>>>>>>>>{}".format(s_action))
        ir_config = request.env['ir.config_parameter'].sudo()
        if kw.get('debug') == "1" or kw.get('debug') == "assets" or kw.get('debug') == "assets,tests":
            if kw.get('hsp') == "123456":
                pass
            else :
                return werkzeug.utils.redirect('/web?debug=1')

        return super(HSPHome, self).web_client(s_action=s_action, **kw)

