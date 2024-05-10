from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.service import db, security
import odoo

obj = Home()


class KsDemoLogin(Home):
    @http.route('/web/became/admin', type='http', auth="none", sitemap=False)
    def switch_to_admin(self):
        uid = request.env.context.get('uid')
        for rec in request.env['ks.users'].sudo().search([]):
            if rec.ks_active:
                current_uid = rec.ks_user_id
                rec.ks_active = False
                break
        if current_uid:
            request.env.user = request.env['res.users'].sudo().browse(uid)
            request.env.uid = uid
            uid = request.session.uid = current_uid
            request.env['res.users'].clear_caches()
            request.session.session_token = security.compute_session_token(request.session, request.env)
        return request.redirect(self._login_redirect(uid))

    @http.route('/web/became/user/<int:data>', type='http', auth="none", sitemap=False)
    def switch_to_user(self, data):
        uid = request.env.context.get('uid')
        for rec in request.env['ks.users'].sudo().search([('id', '=', data)]):
            if rec.ks_active:
                for record in request.env['ks.users'].sudo().search([]):
                    record.ks_current_user = False
                rec.ks_current_user = True
                current_uid = request.env['res.users'].sudo().search([('id','=',rec.ks_user_id)]).id
                rec.ks_active = False
                break
        if current_uid:
            uid = request.session.uid = current_uid
            request.env['res.users'].clear_caches()
            request.session.session_token = security.compute_session_token(request.session, request.env)
        return request.redirect(self._login_redirect(uid))

    @http.route('/web/become', type='http', auth='none', sitemap=False)
    def switch_to_superUser(self):
        if odoo.SUPERUSER_ID:
            uid = request.session.uid = odoo.SUPERUSER_ID
            request.env['res.users'].clear_caches()
            request.session.session_token = security.compute_session_token(request.session, request.env)
            return request.redirect(self._login_redirect(uid))
