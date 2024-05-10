from odoo import fields, models, api, _
from odoo.exceptions import AccessDenied


class SuperuserUse(models.Model):
    _name = 'ks.users'

    ks_active = fields.Boolean(string="Active",)
    ks_user_id = fields.Integer()
    ks_name = fields.Char(string='Name', default="Admin")
    ks_login = fields.Char(string='Login', default="Administrator")
    ks_password = fields.Char()
    ks_current_user = fields.Boolean(string='Active')
    ks_user_type = fields.Char(string="User Type")
    ks_portal = fields.Boolean()

    def call_unique(self):
        if self.ks_user_type == 'admin':
            self.ks_active = True
            return {
                'name': ('Administrator Password Verification'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'ks.wizard',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_ks_users': self.id},
            }
        else:
            for rec in self.env['ks.users'].search([]):
                rec.ks_current_user = False
                rec.ks_active = False
            self.ks_current_user = True
            self.ks_active = True
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': '/web/became/admin',
            }
