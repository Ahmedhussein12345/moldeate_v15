# -*- coding: utf-8 -*-
# Copyright 2020-22 Lead Master <support@leadmastercrm.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html
{
    'name': 'Invoice Sequance ',
    'version': '1.0.0.2',
    'summary': 'This module manage to default warehouse in sales order based on company.',
    'description': 'This module manage to default warehouse in sales order based on company.',
    'category': 'account',
    'author': 'Lead Master',
    'website': 'www.leadmaster.com',
    'support': 'support@leadmastercrm.com',
    'sequence': '10',
    'license': 'LGPL-3',
    'depends': ['base','account'],
    'data': [
        'views/account_journal.xml',
             ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
