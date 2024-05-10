# -*- coding: utf-8 -*-
{
    'name': 'UPS Details Tracking',
    'version': '15.0',
    'category': 'Delivery',
    'summary': 'Get the full tracking details from UPS and Display on picking',

    'depends': ['ups_delivery'],

    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking.xml',
    ],

    'author': 'TeqStars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'TeqStars',

    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
