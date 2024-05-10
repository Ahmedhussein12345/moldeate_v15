# -*- coding: utf-8 -*-
{
    'name': 'LM Web Login Page',
    'version': '15.0.1.0.0',
    'summary': 'Customize Login Page',
    'description': 'Customize The Login Page',
    'category': 'website',
    'author': '',
    'company': 'LM',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'web', 'auth_signup'
    ],
    'data': [
        'views/website_templates.xml',
        'views/webclient_templates.xml',
    ],
    'images': [
        'static/description/wavy_25.svg',
        'static/description/lm_bg.jpeg',
        'static/description/lm_hand.jpeg',
        'static/description/blue_18.svg',
        ],
    'assets': {
        'web.assets_frontend': [
            'lm_website_login/static/src/css/web_login_style.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
