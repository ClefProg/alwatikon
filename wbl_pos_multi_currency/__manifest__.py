# -*- coding: utf-8 -*-
#
#################################################################################
# Author      : Weblytic Labs Pvt. Ltd. (<https://store.weblyticlabs.com/>)
# Copyright(c): 2023-Present Weblytic Labs Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
##################################################################################

{
    'name': 'POS Multi-Currency Payment',
    'version': '19.0.1.0.0',
    'summary': """Multi-currency payments, POS Currency conversion, Currency management, Point of sale currency, Currency selection, International sales, Multi-currency transactions, Foreign currency payments, Multicurrency POS, Multiple currency, Cross-border money, Convert foreign currency.""",
    'description': """Multi-currency payments, POS Currency conversion, Currency management, Point of sale currency, Currency selection, International sales, Multi-currency transactions, Foreign currency payments, Multicurrency POS, Multiple currency, Cross-border money, Convert foreign currency.""",
    "category": "Point of Sale",
    'author': 'Weblytic Labs',
    'company': 'Weblytic Labs',
    'website': "https://store.weblyticlabs.com",
    'depends': ['point_of_sale', 'web', 'account', 'website', 'base', 'sale_management'],
    'price': '35.00',
    'currency': 'USD',
    'data': [
        'views/res_config_settings_view.xml',
        'views/pos_payment_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'wbl_pos_multi_currency/static/src/js/payment_screen.js',
            'wbl_pos_multi_currency/static/src/js/multi_currency_popup.js',
            'wbl_pos_multi_currency/static/src/xml/multi_currency_button.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
    'live_test_url': 'https://youtu.be/1jhpWBgjiw0',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
