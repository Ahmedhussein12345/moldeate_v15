from odoo import models, fields, _, api


class KsResUsers(models.Model):
    _inherit = 'res.users'

    # Inherit fields
    ks_favorite_bar = fields.Boolean(string="Show Favorite Apps", default=False)

    ks_list_density = fields.Selection(string="List View Style",
                                       selection=[('Default', 'Default'), ('Comfortable', 'Comfortable'),
                                                  ('Attachment', 'Attachment')],
                                       default='Default')
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=True)
