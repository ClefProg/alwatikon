# -*- coding: utf-8 -*-
{
    'name': "Alwatikon Enhancements",
    'summary': "Alwatikon Enhancements",
    'description': "Alwatikon Enhancements",

    'author': "Websers",
    'website': "https://websers.odoo.com",
    'license': 'OPL-1',

    'category': 'Alwatikon',
    'version': '19.0.1.0.0',

    'depends': [
        'alwatikon_base',
        'point_of_sale',
        'sh_pos_multi_pricelist',
    ],

    'data': [],

    'assets': {
        'point_of_sale._assets_pos': [
            'alwatikon_enhancements/static/src/**/*',
        ],
    },

    'installable': True,
    'application': False,
}
