# -*- coding: utf-8 -*-
{
    'name': 'Odoo Shipping Partners',
    'version': '15.0',
    'summary': '',
    'category': 'Sales',

    'depends': ['delivery', 'product'],
    'data': [
        'views/stock_picking_view.xml',
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/shipping_api_log_view.xml',
        'security/ir.model.access.csv',
    ],

    'images': ['static/description/base_shipping.png'],
    # Author
    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    'demo': [],
    'qweb': ['static/src/xml/dashboard.backend.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
    'price': 9.99,
    'currency': 'EUR',
}
