# -*- coding: utf-8 -*-pack
{

    # App information
    'name': 'Combo Shipping Integration',
    'category': 'Website',
    'version': '12.15.23.2022',
    'summary': """Using Combo Shipping Integration we connect mulitple carrier like ups,usps,dhl,gls and fedex. using combo we generate the label.""",
    'description': """
        Combo Integration helps you to integrate & manage your ups/usps/dhl/gls/fedex account in odoo. manage your Delivery/shipping operations directly from odoo.Export Order To Selected Carrier while Validate Delivery Order.Auto Import Tracking Detail to odoo.
        Generate Label in Odoo..We also Provide the dhl,bigcommerce,shiphero,gls,fedex,usps,easyship,stamp.com,dpd,shipstation,manifest report.
""",

    # Dependencies
    'depends': ['delivery'],
    # Views
    'data': [
        'security/ir.model.access.csv',
        'data/delivery_fedex.xml',
        'data/delivery_dhl.xml',
        'views/res_company.xml',
        'views/delivery_carrier.xml',
        'views/sale_view.xml',
        'views/stock_picking_vts.xml'],

    # Author

    'author': 'Vraja Technologies',
    'website': 'http://www.vrajatechnologies.com',
    'maintainer': 'Vraja Technologies',
    'live_test_url': 'https://www.vrajatechnologies.com/contactus',
    'images': ['static/description/cover.gif'],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': '199',
    'currency': 'EUR',
    'license': 'OPL-1',

}

# 12.15.11.21 Latest Version
