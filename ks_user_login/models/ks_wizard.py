from odoo import fields, models, api, _
from odoo.exceptions import AccessDenied


class SuperuserWizard(models.Model):
    _name = 'ks.wizard'

    ks_password = fields.Char()
    ks_users = fields.Many2one('ks.users')

    def cancel_func(self):
        for rec in self.env['ks.users'].search([('ks_active', '=', True)]):
            rec.ks_active = False

    def callable_func(self):
        db = self.pool.db_name
        rec = self.ks_users
        admin = self.env['res.users'].search([('id', '=', rec.ks_user_id)])
        uid = self.env['res.users'].password_check(admin, db, self.ks_password)
        if uid:
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': '/web/became/user/%s' % (rec.id),
            }
