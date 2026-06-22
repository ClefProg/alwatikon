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
    usd_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_usd_currency_id',
        string='USD Currency',
    )
    current_usd_cost = fields.Float(
        string='Current USD Cost',
        company_dependent=True,
        groups='alwatikon_pricing.group_pricing_accounting_admin',
        default=False,
        help=(
            'Current USD cost used for pricing decisions. '
            'Does not affect standard_price or inventory valuation.'
        ),
    )

    def _compute_usd_currency_id(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            record.usd_currency_id = usd_currency and usd_currency.id or False
