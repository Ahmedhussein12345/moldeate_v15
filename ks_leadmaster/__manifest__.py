# -*- coding: utf-8 -*-
{
    'name': "Base LeadMaster Settings",

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

    'author': "LeadMaster",
    'website': "LeadMaster.com",
    'version': "2022.0.3",

    # any module necessary for this one to work correctly
    'depends': ['crm', 'ks_curved_backend_theme', 'arc_leadmaster', 'sh_global_search',
                'global_search', 'odoo_recently_viewed_records', 'ye_dynamic_odoo',
                'app_odoo_customize'],


    'assets': {
        'web.assets_frontend': [
            '/ks_leadmaster/static/src/scss/ks_global_module.scss',
        ],
    },
    "application": True,
    "installable": True,
}
