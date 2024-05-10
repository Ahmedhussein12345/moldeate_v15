import odoo
from odoo import api, fields, models, modules, tools, _


ACTION_DICT = {
    'view_type': 'form',
    'view_mode': 'form',
    'res_model': 'base.module.upgrade',
    'target': 'new',
    'type': 'ir.actions.act_window',
}


class IrModuleInherited(models.Model):
    _inherit = 'ir.module.module'

    def button_install(self):
        super(IrModuleInherited, self).button_install()
        for rec in self:
            if rec.shortdesc == 'Website':
                user_login = rec.pool.models.get('ks.wizard')
                if user_login is not None:
                    for record in rec.env['ks.users'].search(
                            ['|', ('ks_user_type', '=', 'portal'), ('ks_user_type', '=', '')]):
                        record.ks_portal = False
        return dict(ACTION_DICT, name=_('Install'))

    def button_uninstall(self):
        super(IrModuleInherited, self).button_uninstall()
        for rec in self:
            if rec.shortdesc == 'Website':
                user_login = rec.pool.models.get('ks.wizard')
                if user_login is not None:
                    for record in self.env['ks.users'].search(
                            ['|', ('ks_user_type', '=', 'portal'), ('ks_user_type', '=', '')]):
                        record.ks_portal = True
        return dict(ACTION_DICT, name=_('Uninstall'))
