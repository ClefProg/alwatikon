# -*- coding: utf-8 -*-
{
    'name': "Alwatikon Pricing",
    'summary': "Alwatikon Pricing",
    'description': "Alwatikon Pricing",

    'author': "Websers",
    'website': "https://websers.odoo.com",
    'license': 'OPL-1',

    'category': 'Alwatikon',
    'version': '19.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['alwatikon_base', 'product', 'stock_account', 'accountant', 'sale_management', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/product_display_name_views.xml',
        'views/product_product_views.xml',
        'views/usd_cost_log_views.xml',
    ],

    'installable': True,
    'application': False,

}


