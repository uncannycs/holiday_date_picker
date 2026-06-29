# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Uncanny Consulting Services LLP
#    Copyright (C) 2023 Uncanny Consulting Services LLP (<https://uncannycs.com>).
#
##############################################################################
{
    'name': 'Holiday Date Picker',
    'version': '19.0.1.0.3',
    "author": "Uncanny Consulting Services LLP",
    "website": "https://uncannycs.com",
    'category': 'Sales',
    'summary': 'Add promise date on sale order, restrict holidays selection',
    'depends': ['sale', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/holiday_date_views.xml',
        'views/holiday_field_config_views.xml',
        'views/sale_order_line_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'holiday_date_picker/static/src/js/holiday_date_field.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
