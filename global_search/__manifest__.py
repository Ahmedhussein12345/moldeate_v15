# -*- coding: utf-8 -*-
{
    'name': "Arc Global Search",

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
    'depends': ['base','sh_global_search'],

    # always loaded
    'data': [
        'views/ks_global_search_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'assets': {
        # Q-WEB Files Link
        'web.assets_qweb': [
            'global_search/static/src/xml/lm_global_search.xml',
            'global_search/static/src/xml/lm_search_page.xml',

        ],
        'web._assets_primary_variables': [
        ],
        # SCSS and JS Files Link
        'web.assets_backend': [
            'global_search/static/src/scss/ks_search_bar.scss',

            'global_search/static/src/js/ks_lm_control_panel.js',
            'global_search/static/src/js/ks_apps_inherit.js',
        ],
        'web.assets_frontend': [
        ],

    },

    "application": True,
    "installable": True,
}
