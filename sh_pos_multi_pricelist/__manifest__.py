# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Point Of Sale Multi Currency Pricelist",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Point Of Sale",
    "license": "OPL-1",

    "summary": "Point Of Sale Multi Currency Pricelist Odoo POS Different Currency Point Of Sale Multi Pricelist POS Multi-Currency Payment POS Multiple Currency Module Point Of Sale Various Currency Pricelist Allow Multi Currencies Pricelist In POS Pricelist Management Odoo POS Different Currency POS Multi-Currency App Point Of Sale Multi Pricelist Point Of Sale Various Currency Pricelist POS Multi-Currency Payment POS Multiple Currency Modulet POS Pricelist Management Odoo POS Multi Currency Pricelist Odoo Point Of Sale Different Currency POS Multi Pricelist Point Of Sale Multi-Currency Payment Point Of Sale Multiple Currency Module POS Various Currency Pricelist Allow Multi Currencies Pricelist In Point Of Sale Pricelist Management Odoo Point Of Sale Different Currency Point Of Sale Multi-Currency App POS Multi Pricelist Point Of Sale Multi-Currency Payment Point Of Sale Multiple Currency Modulet Point Of Sale Pricelist Management Odoo Price Change on Currency Rate POS Price Change on Currency Rate Point of Sale Price Change on Currency Rate",

    "description": """By default, odoo provides only a single currency in the POS. This module supports a multi-currency pricelist in the point of sale. If the user selects the different currency's pricelist then pricelist currency and price changed based on the currency. You can print a POS receipt with a different currency.""",
    "version": "19.0.2.0.4",
    "depends": ["point_of_sale"],
    "application": True,
    "data": [
        "views/res_config_settings_view.xml",
    ],
    'assets': {'point_of_sale._assets_pos': [
        'web/static/lib/jquery/jquery.js',
        'sh_pos_multi_pricelist/static/src/**/*',
    ],
    },
    "auto_install": False,
    "installable": True,
    "price": 29,
    "currency": "EUR",
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/4M0J6kHFsMA",
}
