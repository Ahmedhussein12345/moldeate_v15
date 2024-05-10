from odoo import api, models, fields

class ResUsers(models.Model):

    _inherit = "res.users"

    notification_type = fields.Selection(lambda self: self.dynamic_selection(),
                                         'Notification', required=True, default='email')

    def dynamic_selection(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        app_system_name = ir_config.get_param('app_system_name', default='odooApp')
        select = [
        ('email', 'Handle by Emails'),
        ('inbox', 'Handle in %s'%app_system_name)]

        return select

    def preference_change_password(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        app_system_name = ir_config.get_param('app_system_name', default='odooApp')
        return {
            'name': '%s'%app_system_name,
            'type': 'ir.actions.client',
            'tag': 'change_password',
            'target': 'new',
        }
    odoobot_state = fields.Selection(
        [
            ('not_initialized', 'Not initialized'),
            ('onboarding_emoji', 'Onboarding emoji'),
            ('onboarding_attachement', 'Onboarding attachement'),
            ('onboarding_command', 'Onboarding command'),
            ('onboarding_ping', 'Onboarding ping'),
            ('idle', 'Idle'),
            ('disabled', 'Disabled'),
        ], string="OdooBot Status", readonly=True, required=False,default=lambda self: self.default_odoobot())  # keep track of the state: correspond to the code of the last message sent

    def default_odoobot(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        odoobot_state = ir_config.get_param('odoobot_state')

        return odoobot_state