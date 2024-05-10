# -*- encoding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

{
    'name': 'Sale Order Extend Report',
    'version': '15.0.1.1',
    'author': 'Lead Master',
    'maintainer': 'Lead Master',
    'website': 'www.leadmaster.com',
    'support': 'support@leadmastercrm.com',
    'license': 'LGPL-3',
    'category': 'Report',
    'summary': 'Sale Order Extend Report',
    'description': 'Sale Order Extend Report',
    'depends': ['sale_management', 'account','sales_product_count','stock'],
    'data': [
        'views/report_sale_order_custom.xml',
        'views/report_action.xml',
        'views/international_report_template.xml',
        'views/domestic_invoice_report.xml',
        'views/invoice_report_action.xml',
        'views/international_invoice_report.xml',
        'views/delivery_order.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
