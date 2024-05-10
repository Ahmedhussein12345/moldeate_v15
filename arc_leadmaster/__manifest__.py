# -*- coding: utf-8 -*-
{
    'name': "Arc LeadMaster",

    'summary': """
        Ditch the boring theme while working; opt for the Odoo Arc Backend Theme and increase your business performance.
        Switch from Light and Dark mode as per your working necessities. Arc Backend Theme, Backend Theme, Responsive Theme, 
        Fully Functional Theme, Flexible Backend Theme, Fast Backend Theme, Modern Multipurpose Theme, Lightweight Backend Theme, 
        Animated Backend Theme, Advance Material Backend Theme, Customizable Backend Theme, Multi Tab Backend Theme Odoo, 
        Attractive Theme for Backend, Elegant Backend Theme, Community Backend Theme, Odoo Community Backend Theme, 
        Fully Functional Backend Theme, Responsive Web Client, Mobile Theme, Backend UI, Mobile Interface,
        Mobile Responsive for Odoo Community, Dual Color Backend Theme, Flexible Enterprise Theme, Enterprise Backend Theme
    """,
    'description': """
        odoo backend themes
        odoo responsive backend theme
        odoo themes
        odoo backend theme V15
        odoo 15 backend theme
        backend theme odoo
        odoo enterprise theme
        odoo custom themes
        odoo theme download
        change odoo backend theme
        odoo material backend theme
        odoo theme backend
        backend theme odoo apps
        odoo backend theme customize
        change backend theme odoo
        odoo backend layout theme
        customizable odoo Theme
        customize odoo backend
        change odoo backend color
        odoo app backend theme
        Arc Theme
	    Arc Themes
	    Backend Theme
        Backend Themes
        Curved Theme
	    Boxed Theme
    	Curved Backend Theme
	    Odoo Arc Theme
	    Odoo Arc Backend Theme
	    Odoo Arc
	    Odoo Backend Theme
	    Ksolves Arc
	    Ksolves Arc Theme
	    Ksolves Arc Backend Theme
	    Ksolves Odoo Theme
	    Ksolves Odoo Backend Theme
	    Ksolves Backend Theme
	    Ksolves Themes
    """,

    'author': "Ksolves India Ltd.",
    'website': "https://www.ksolves.com",
    'license': 'OPL-1',
    'version': '1.0.1',
    'live_test_url': 'https://arcbackendtheme15.kappso.com/web/demo_login',
    'category': 'Themes/Backend',
    'support': 'sales@ksolves.com',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'base_setup', 'mail', 'auth_signup', 'ks_curved_backend_theme'],

    # always loaded
    'data': [
        'security/arc_lm_security.xml',
        'data/data.xml',
        'data/ks_lead_color_theme.xml',
    ],

    'assets': {
        # Q-WEB Files Link
        'web.assets_qweb': [
            'arc_leadmaster/static/src/xml/ks_lm_navbar.xml',
            'arc_leadmaster/static/src/xml/ks_lm_global_settings.xml',
            'arc_leadmaster/static/src/xml/ks_lm_quick_settings.xml',
        ],

        # SCSS and JS Files Link
        'web.assets_backend': [
            'arc_leadmaster/static/src/scss/top_bar.scss',

            'arc_leadmaster/static/src/js/ks_control_panel.js',
            'arc_leadmaster/static/src/js/ks_search_bar.js',
            'arc_leadmaster/static/src/js/ks_lm_navbar.js',
            'arc_leadmaster/static/src/js/ks_lm_app_sidebar.js',
        ],
    },

    "application": True,
    "installable": True,
    'post_init_hook': '_post_init_hook',
}
