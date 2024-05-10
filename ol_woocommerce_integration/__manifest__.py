# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Woocommerce Custom",

    "author": "Huzaifa",
    "category": "Extra Tools",

    "license": "OPL-1",

    "version": "15.0.1",

    "depends": [
        'sale',
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/main_view.xml',
        # 'views/sub_instances.xml',
        'views/ext.xml',
        # 'static/icons/woocommerce_icon.ico'
    ],
    "images": [ ],
    "auto_install": False,
    "application": True,
    "installable": True,
    "price": "60",
    "currency": "EUR",
    'web': {
        'routes': {
            'controller_name': [
                '/my_module/get_attachment/<string:attachment_id>',
                'AttachmentController.get_attachment',
            ],
        },
    }
}
