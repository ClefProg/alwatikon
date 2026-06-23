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
    'depends': ['alwatikon_base', 'product', 'stock_account', 'accountant', 'sale_management', 'mail', 'purchase', 'point_of_sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/pricing_pricelists_data.xml',
        'data/pricing_defaults_data.xml',
        'data/pricing_export_data.xml',
        'views/res_config_settings_views.xml',
        'views/product_display_name_views.xml',
        'views/product_product_views.xml',
        'views/product_pricelist_views.xml',
        'views/pricing_record_views.xml',
        'views/usd_cost_log_views.xml',
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            'alwatikon_pricing/static/src/js/pos_store.js',
        ],
    },

    'installable': True,
    'application': False,

}


