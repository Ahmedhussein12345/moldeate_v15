# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
{
    'name': 'Default Warehouse Based on Company',
    'version': '1.0.0.0',
    'summary': 'This module manage to default warehouse in sales order based on company.',
    'description': 'This module manage to default warehouse in sales order based on company.',
    'category': 'sales',
    'author': 'Lead Master',
    'website': 'www.leadmaster.com',
    'support': 'support@leadmastercrm.com',
    'sequence': '10',
    'license': 'LGPL-3',
    'depends': ['base', 'stock', 'sale','sale_stock','sale_order_line_by_warehouse_app','account'],
    'data': [
        'views/res_company.xml',
        'views/stock_warehouse.xml'
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
