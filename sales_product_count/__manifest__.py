# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
{
    'name': 'Sales Order Product Count',
    'version': '1.0.0.0',
    'summary': 'This module mainly used to calculate the order line product count in sales order.',
    'description': 'This module mainly used to calculate the order line product count in sales order.',
    'category': 'sales',
    'author': 'Lead Master',
    'website': 'www.leadmaster.com',
    'support': 'support@leadmastercrm.com',
    'sequence': '10',
    'license': 'LGPL-3',
    'depends': ['sale','sale_management','account'],
    'data': [
        'views/sales_order.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
