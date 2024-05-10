# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions



class KsThemeGlobalConfig(models.Model):
    _inherit = "ks.global.config"

    # Inherit fields
    ks_favorite_bar = fields.Boolean(string="Show Favorite Apps", default=False)

    ks_list_density = fields.Selection(string="List View Style",
                                       selection=[('Default', 'Default'), ('Comfortable', 'Comfortable'),
                                                  ('Attachment', 'Attachment')],
                                       default='Default')

    ks_click_edit = fields.Boolean(string="Double-click Edit", default=True)
    ks_company_logo_enable = fields.Boolean(string="Enable Company Logo", default=True)
    ks_loaders = fields.Selection(string="Loading Bar", selection=[('ks_loader_1', 'Loader 1'),
                                                                   ('ks_loader_2', 'Loader 2'),
                                                                   ('ks_loader_3', 'Loader 3'),
                                                                   ('ks_loader_4', 'Loader 4'),
                                                                   ('ks_loader_5', 'Loader 5'),
                                                                   ('ks_loader_6', 'Loader 6'),
                                                                   ('ks_loader_7', 'Loader 7'),
                                                                   ('ks_loader_default', 'Default Loader'),
                                                                   ], default='ks_loader_4')

    ks_login_page_style = fields.Selection(string="Login Page Style",
                                           selection=[('default', 'Default'), ('Style1', 'Style1'), ('Style2', 'Style2'), ('Style3', 'Style3'),
                                                      ('Style4', 'Style4'), ('Style5', 'Style5')], default='Style5')

    ks_chatter = fields.Selection(string="Chatter Position",
                                  selection=[('ks_chatter_bottom', 'Bottom'), ('ks_chatter_right', 'Right')],
                                  default='ks_chatter_right')

    ks_website_title = fields.Char(string="Website Backend Title", default='SuiteMaster')
    ks_website_title_enable = fields.Boolean(string="Enable Website Backend Title", default='True')
    ks_company_logo_enable = fields.Boolean(string="Enable Company Logo", default='True')


    # ---- Scope ---- #
    # FixMe: Single scope fields can be displayed as dummy for now only on  HTML

    scope_ks_auto_dark_mode = fields.Selection(
        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')], default='Global')
    scope_ks_list_density = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_click_edit = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='Global')
    scope_ks_menu_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                         default='Global')
    scope_ks_favorite_bar = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_chatter = fields.Selection(selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='Global')
    scope_ks_website_title = fields.Selection(string="Scope of Website Backend Title",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')], default='Global')
    scope_ks_favicon = fields.Selection(string="Scope of Favicon",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='Global')
    scope_ks_company_logo = fields.Selection(string="Scope of company logo",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_small_company_logo = fields.Selection(string="Scope of small company logo",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')], default='Global')
    scope_ks_enterprise_apps = fields.Selection(string="Scope of Enterprise Apps",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='Global')
    scope_ks_odoo_referral = fields.Selection(string="Scope of Odoo referral",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')],
                                              default='Global')
    scope_ks_theme_style = fields.Selection(string="Scope of Theme Style",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='Global')
    scope_ks_colors_theme = fields.Selection(string="Scope of Colors Theme",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_font_style = fields.Selection(string="Scope of Font Style",
                                           selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                           default='Global')
    scope_ks_button_style = fields.Selection(string="Scope of Button style",
                                             selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                             default='Global')
    scope_ks_body_background = fields.Selection(string="Scope of Body background",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='Global')

    scope_ks_app_drawer_background = fields.Selection(string="Scope of App Drawer background",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='Global')

    scope_ks_separator_style = fields.Selection(string="Scope of Seperator Style",
                                                selection=[('User', 'User'), ('Company', 'Company'),
                                                           ('Global', 'Global')],
                                                default='Global')
    scope_ks_tab_style = fields.Selection(string="Scope of Tab Style",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='Global')
    scope_ks_checkbox_style = fields.Selection(string="Scope of Checkbox Style",
                                               selection=[('User', 'User'), ('Company', 'Company'),
                                                          ('Global', 'Global')],
                                               default='Global')
    scope_ks_popup_animation_style = fields.Selection(string="Scope of Animation Style",
                                                      selection=[('User', 'User'), ('Company', 'Company'),
                                                                 ('Global', 'Global')],
                                                      default='Global')
    scope_ks_loaders = fields.Selection(string="Scope of Loaders",
                                        selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                        default='Global')
    scope_ks_icon_design = fields.Selection(string="Scope of Icon Design",
                                            selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                            default='Global')
    scope_ks_login_page_style = fields.Selection(string="Scope of Login Style",
                                                 selection=[('User', 'User'), ('Company', 'Company'),
                                                            ('Global', 'Global')],
                                                 default='Global')
    scope_ks_login_background_image = fields.Selection(string="Scope of Login Background",
                                                       selection=[('User', 'User'), ('Company', 'Company'),
                                                                  ('Global', 'Global')],
                                                       default='Global')
    scope_ks_header = fields.Selection(string="Scope of Header",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='Global')
    scope_ks_footer = fields.Selection(string="Scope of Footer",
                                       selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                       default='Global')

    scope_ks_font_size = fields.Selection(string="Scope of Font Size",
                                          selection=[('User', 'User'), ('Company', 'Company'), ('Global', 'Global')],
                                          default='Global')
    scope_ks_radio_button_style = fields.Selection(string="Scope of Radio Button Style",
                                                   selection=[('User', 'User'), ('Company', 'Company'),
                                                              ('Global', 'Global')],
                                                   default='Global')

    # Note: these fields are created only for user scopes.
    scope_ks_favtbar_autohide = fields.Selection(string="Scope of Favorite bar auto hide",
                                                 selection=[('User', 'User'), ('Company', 'Company'),
                                                            ('Global', 'Global')],
                                                 default='Global')
    scope_ks_favtbar_position = fields.Selection(string="Scope of Favorite bar position",
                                                 selection=[('User', 'User'), ('Company', 'Company'),
                                                            ('Global', 'Global')],
                                                 default='Global')
    scope_ks_show_app_name = fields.Selection(string="Scope of Apps name show",
                                              selection=[('User', 'User'), ('Company', 'Company'),
                                                         ('Global', 'Global')],
                                              default='Global')
    scope_ks_user_menu_placement = fields.Selection(string="Scope of Apps menu placement",
                                                    selection=[('User', 'User')],
                                                    default='User')
    scope_ks_menubar_autohide = fields.Selection(string="Scope of Apps menubar auto hide",
                                                 selection=[('User', 'User')],
                                                 default='User')

    ks_body_background_image_enable = fields.Boolean(string="Enable body background images", default=False)

