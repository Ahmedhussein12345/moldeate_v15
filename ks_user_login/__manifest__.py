# -*- coding: utf-8 -*-
{
	'name': 'Allow Login as Any User',

	'summary': """
Now, it is very easy for the users to switch and login to any user’s account without typing in any password. There is a Login button provided for this through which the user can access any other individual’s account.
""",

	'description': """
odoo allow any user login app,
     allow any user login odoo,
     odoo apps,
     odoo login,
     odoo sign up,
     odoo sign in,
     user allow any user login module,
     allow any user login module,
     allow any user login app,
      user login, 
    login security, 
    odoo login , 
    odoo user login,
    odoo admin login, 
    odoo admin session, 
    user login security, 
    login screen app, 
    odoo login app, 
    odoo login screen app, 
    odoo login module,
""",

	'author': 'Ksolves India Pvt. Ltd.',

	'website': 'https://www.ksolves.com/',

	'live_test_url': 'http://userlogin.kappso.in/',

	'category': 'Sales',

	'application': True,

	'license': 'OPL-1',

	'currency': 'EUR',

	'price': 20.0,

	'maintainer': 'Ksolves India Pvt. Ltd.',

	'support': 'sales@ksolves.com',

	'images': ['static/description/event_banner.gif'],

	'version': '15.0.1.1.0',

	'depends': ['base', 'web'],

	'data': ['security/ir.model.access.csv', 'views/ks_admin_user.xml', 'views/ks_wizard.xml'],

	'post_init_hook': 'post_install_hook',
}
