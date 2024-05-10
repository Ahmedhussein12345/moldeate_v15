{
    'name': 'UPS Odoo Shipping Connector',
    'version': '15.1',
    'category': 'Warehouse',
    'summary': 'Integrate & Manage your UPS Shipping Operation from Odoo',
    'depends': ['base_shipping_partner'],

    'data': [
        'data/stock_package_type_ups.xml',
        'views/delivery_carrier_view.xml',
        'views/shipping_partner_view.xml',
     ],

    'images': ['static/description/ups_odoo.png'],

    'author': 'Teqstars',
    'website': 'https://teqstars.com',
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your UPS operation from Odoo
        - Integration UPS
        - Connector UPS
        - UPS Connector
        - Odoo UPS Connector
        - UPS integration
        - UPS odoo connector
        - UPS odoo integration
        - UPS shipping integration
        - UPS integration with Odoo
        - odoo integration apps
        - odoo UPS integration
        - odoo integration with UPS
        - shipping integration
        - shipping provider integration
        - shipper integration
    """,

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'price': '90.00',
    'currency': 'EUR',

}
