from odoo import fields, models, api
from odoo.http import request
from odoo.addons.web.controllers.main import http


class Superuser(models.Model):
    _inherit = 'res.users'

    def active_user(self):
        return http.request.context.get('uid')

    @api.model_create_multi
    def create(self, vals_list):
        ks_user_type = ''
        portal_group_id = self.env['res.groups'].search([('name', '=', 'Portal')]).id
        internal_group_id = self.env['res.groups'].search([('name', '=', 'Internal User')]).id
        public_group_id = self.env['res.groups'].search([('name', '=', 'Public')]).id
        admin_group_id_1 = self.env['res.groups'].search([('name', '=', 'Settings')]).id
        admin_group_id_2 = self.env['res.groups'].search([('name', '=', 'Access Rights')]).id
        user = super(Superuser, self).create(vals_list)
        if (admin_group_id_1 in user.groups_id.ids) or (admin_group_id_2 in user.groups_id.ids):
            ks_user_type = 'admin'
        elif portal_group_id in user.groups_id.ids:
            ks_user_type = 'portal'
        elif internal_group_id in user.groups_id.ids:
            ks_user_type = 'demo'
        elif public_group_id in user.groups_id.ids:
            ks_user_type = 'public'
        list = {
            'ks_name': user.name,
            'ks_login': user.login,
            'ks_user_id': user.id,
            'ks_user_type': ks_user_type,
        }
        self.env['ks.users'].create(list)
        return user

    def write(self, values):
        res = super(Superuser, self).write(values)
        portal_group_id = self.env['res.groups'].search([('name', '=', 'Portal')]).id
        internal_group_id = self.env['res.groups'].search([('name', '=', 'Internal User')]).id
        public_group_id = self.env['res.groups'].search([('name', '=', 'Public')]).id
        admin_group_id_1 = self.env['res.groups'].search([('name', '=', 'Settings')]).id
        admin_group_id_2 = self.env['res.groups'].search([('name', '=', 'Access Rights')]).id
        for records in self:
            portal = self.pool.models.get('website.menu')
            user_login = self.pool.models.get('ks.wizard')
            if user_login is not None:
                if portal is None:
                    for rec in self.env['ks.users'].search([('ks_user_type', '=', 'portal')]):
                        rec.ks_portal = True
                else:
                    for rec in self.env['ks.users'].search([('ks_user_type', '=', 'portal')]):
                        rec.ks_portal = False
            ks_user_type = ''
            if (admin_group_id_1 in records.groups_id.ids) or (admin_group_id_2 in records.groups_id.ids):
                ks_user_type = 'admin'
            elif portal_group_id in records.groups_id.ids:
                ks_user_type = 'portal'
            elif internal_group_id in records.groups_id.ids:
                ks_user_type = 'demo'
            elif public_group_id in records.groups_id.ids:
                ks_user_type = 'public'
            list = {
                'ks_name': records.name,
                'ks_login': records.login,
                'ks_user_type': ks_user_type,
            }
            self.env['ks.users'].search([('ks_user_id', '=', records.id)]).update(list)
        return res

    def unlink(self):
        for rec in self:
            find_id = self.env['ks.users'].search([('ks_user_id', '=', rec.id)])
            find_id.unlink()
        super(Superuser, self).unlink()

    def password_check(self, admin, db, password):
        wsgienv = request.httprequest.environ
        env = dict(
            base_location=request.httprequest.url_root.rstrip('/'),
            HTTP_HOST=wsgienv['HTTP_HOST'],
            REMOTE_ADDR=wsgienv['REMOTE_ADDR'],
        )
        uid = admin.authenticate(db, admin.login, password, env)
        return uid

    @api.model
    def _get_login_domain(self, login):
        super(Superuser, self)._get_login_domain(login)
        id = self.env['res.users'].search([('login', '=', login)]).id
        for rec in self.env['res.users'].search([]):
            rec.user_id = id
        for rec in self.env['ks.users'].search([]):
            rec.ks_current_user = False
        portal = self.pool.models.get('website.menu')
        user_login = self.pool.models.get('ks.wizard')
        if user_login is not None:
            if portal is None:
                for rec in self.env['ks.users'].search([('ks_user_type', '=', 'portal')]):
                    rec.ks_portal = True
            else:
                for rec in self.env['ks.users'].search([('ks_user_type', '=', 'portal')]):
                    rec.ks_portal = False
        self.env['ks.users'].search([('ks_login', '=', login)]).ks_current_user = True
        return [('login', '=', login)]
