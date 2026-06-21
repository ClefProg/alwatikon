# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricing_channel = fields.Selection(
        selection=[
            ('wholesale_usd', 'Wholesale USD'),
            ('wholesale_lyd', 'Wholesale LYD'),
            ('wholesale_bank', 'Wholesale Bank'),
            ('retail_usd', 'Retail USD'),
            ('retail_lyd', 'Retail LYD'),
            ('retail_bank', 'Retail Bank'),
            ('retail_bnz', 'Retail BNZ'),
        ],
        string='Pricing Channel',
        copy=False,
        help='Identifies this pricelist for pricing-record publish (one channel per pricelist).',
    )
