from . import models
from . import controller



from odoo.api import Environment, SUPERUSER_ID


def post_install_hook(cr, registry):
    """
    This will provide access of the module to the existing users at the time of installation.
    """

    env = Environment(cr, SUPERUSER_ID, {})
    vals = []
    ks_portal = False
    current_user = env['res.users'].active_user()
    portal_group_id = env['res.groups'].search([('name', '=', 'Portal')]).id
    internal_group_id = env['res.groups'].search([('name', '=', 'Internal User')]).id
    public_group_id = env['res.groups'].search([('name', '=', 'Public')]).id
    admin_group_id_1 = env['res.groups'].search([('name', '=', 'Settings')]).id
    admin_group_id_2 = env['res.groups'].search([('name', '=', 'Access Rights')]).id
    portal = env.registry.models.get('website.menu')
    if portal is None:
        ks_portal = True
    else:
        ks_portal = False
    for rec in env['res.users'].search([]):
        ks_user_type = ''
        current_user_1 = False
        for record in rec.groups_id:
            if record.id in (admin_group_id_1,admin_group_id_2):
                ks_user_type = 'admin'
                portal = False
                if rec.id == current_user:
                    current_user_1 = True
                else:
                    current_user_1 = False
                break
            elif record.id == portal_group_id:
                # ks_user_type = 'portal'
                ks_user_type = record.name
                current_user_1 = False
                if ks_portal is True:
                    portal = True
                else:
                    portal = False
                break
            elif record.id == internal_group_id:
                # ks_user_type = 'demo'
                ks_user_type = record.name
                current_user_1 = False
                portal = False
                break
            elif record.id == public_group_id:
                # ks_user_type = 'public'
                ks_user_type = record.name
                current_user_1 = False
                portal = False
                break
        list = {
            'ks_name': rec.name,
            'ks_login': rec.login,
            'ks_user_id': rec.id,
            'ks_user_type': ks_user_type,
            'ks_portal': portal,
            'ks_current_user': current_user_1,
        }
        vals.append(list)
    env['ks.users'].create(vals)