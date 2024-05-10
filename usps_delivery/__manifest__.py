# -*- coding: utf-8 -*-
{
    'name': 'USPS Odoo Shipping Connector',
    'version': '15.0',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your USPS Shipping Operations from Odoo',

    'depends': ['base_shipping_partner'],

    'data': [
        'views/shipping_partner_view.xml',
        'views/delivery_carrier_view.xml',
        'views/stock_package_type_view.xml',
        'views/usps_request_templates.xml',
    ],

    'images': ['static/description/usps_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your USPS operation from Odoo
        - Integration USPS
        - Connector USPS
        - USPS Connector
        - Odoo USPS Connector
        - USPS integration
        - USPS odoo connector
        - USPS odoo integration
        - USPS shipping integration
        - USPS integration with Odoo
        - odoo integration apps
        - odoo USPS integration
        - odoo integration with USPS
        - shipping integation
        - shipping provider integration
        - shipper integration
        - USPS shipping 
        - USPS delivery
        - USPS, UPS, FedEx, DHL eCommerce, DHL Express, LaserShip, OnTrac, GSO, APC, Aramex, ArrowXL, Asendia, Australia Post, AxlehireV3, BorderGuru, Cainiao, Canada Post
, Canpar, CDL Last Mile Solutions, Chronopost, Colis Privé, Colissimo, Correios, CouriersPlease, Dai Post, Deliv, Deutsche Post, DPD UK, DPD
        """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '99.00',
    'currency': 'EUR',
}
