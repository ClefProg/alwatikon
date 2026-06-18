# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    display_name_id = fields.Many2one(
        'product.display.name',
        index=True,
        string='Marketing Display Name',
        ondelete='set null'
    )
    current_usd_cost = fields.Float(
        string='Current USD Cost',
        company_dependent=True,
        digits='Product Price',
        groups='alwatikon_pricing.group_pricing_accounting_admin',
        help=(
            'Current USD cost used for pricing decisions. '
            'Does not affect standard_price or inventory valuation.'
        ),
    )