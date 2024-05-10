from odoo import models, fields


class KsResCompany(models.Model):
    _inherit = 'res.company'
    # ToDo: Add Default Values and strings

    # Inherit fields
    ks_favorite_bar = fields.Boolean(string="Show Favorite Apps", default=False)

    ks_list_density = fields.Selection(string="List View Style",
                                       selection=[('Default', 'Default'), ('Comfortable', 'Comfortable'),
                                                  ('Attachment', 'Attachment')],
                                       default='Default')
    ks_click_edit = fields.Boolean(string="Double-click Edit", default=True)
    ks_company_logo_enable = fields.Boolean(string="Enable Company Logo", default=True)