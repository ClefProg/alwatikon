# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_is_zero


class PricingRecordLine(models.Model):
    _name = 'pricing.record.line'
    _description = 'Pricing Record Line'
    _order = 'display_name_id'

    record_id = fields.Many2one(
        'pricing.record',
        string='Pricing Record',
        required=True,
        ondelete='cascade',
        index=True,
    )
    company_id = fields.Many2one(
        related='record_id.company_id',
        store=True,
        index=True,
    )
    display_name_id = fields.Many2one(
        'product.display.name',
        string='Display Name',
        required=True,
    )
    cost = fields.Float(
        string='Cost (USD)',
        compute='_compute_cost',
        store=False,
        digits='Product Price',
    )
    wholesale_usd_price = fields.Float(
        string='Wholesale USD Price',
        digits='Product Price',
    )
    retail_usd_price = fields.Float(
        string='Retail USD Price',
        digits='Product Price',
    )
    wholesale_rate = fields.Float(
        related='record_id.wholesale_pricing_rate',
    )
    retail_rate = fields.Float(
        related='record_id.retail_pricing_rate',
    )
    wholesale_lyd_price = fields.Float(
        string='Wholesale LYD Price',
        compute='_compute_prices',
        store=False,
        digits='Product Price',
    )
    retail_lyd_price = fields.Float(
        string='Retail LYD Price',
        compute='_compute_prices',
        store=False,
        digits='Product Price',
    )
    wholesale_bank_price = fields.Float(
        string='Wholesale Bank Price',
        compute='_compute_prices',
        store=False,
        digits='Product Price',
    )
    retail_bank_price = fields.Float(
        string='Retail Bank Price',
        compute='_compute_prices',
        store=False,
        digits='Product Price',
    )
    retail_bnz_price = fields.Float(
        string='Retail BNZ Price',
        compute='_compute_prices',
        store=False,
        digits='Product Price',
    )
    last_published_cost = fields.Float(
        string='Last Published Cost',
        digits='Product Price',
        copy=False,
        help='Cost snapshot taken at the last publish.',
    )
    cost_changed_recently = fields.Boolean(
        string='Cost Changed Recently',
        compute='_compute_cost_changed_recently',
        store=False,
    )

    _sql_constraints = [
        (
            'record_display_name_unique',
            'unique(record_id, display_name_id)',
            'Each display name can only appear once per pricing record.',
        ),
    ]

    @api.depends('display_name_id', 'display_name_id.variant_ids', 'company_id')
    def _compute_cost(self):
        for line in self:
            cost = 0.0
            if line.display_name_id:
                variants = line.display_name_id.variant_ids.with_company(line.company_id)
                total_qty = sum(variants.mapped('qty_available'))
                if total_qty:
                    weighted = sum(
                        variant.current_usd_cost * variant.qty_available
                        for variant in variants
                    )
                    cost = weighted / total_qty
            line.cost = cost
            line.wholesale_usd_price = cost
            line.retail_usd_price = cost

    @api.depends(
        'wholesale_usd_price',
        'retail_usd_price',
        'record_id.wholesale_pricing_rate',
        'record_id.retail_pricing_rate',
        'record_id.bank_markup',
        'record_id.eastern_region_markup',
    )
    def _compute_prices(self):
        for line in self:
            record = line.record_id
            wholesale_lyd = line.wholesale_usd_price * record.wholesale_pricing_rate
            retail_lyd = line.retail_usd_price * record.retail_pricing_rate
            bank_factor = 1.0 + record.bank_markup
            bnz_factor = 1.0 + record.eastern_region_markup

            line.wholesale_lyd_price = wholesale_lyd
            line.retail_lyd_price = retail_lyd
            line.wholesale_bank_price = wholesale_lyd * bank_factor
            line.retail_bank_price = retail_lyd * bank_factor
            line.retail_bnz_price = retail_lyd * bnz_factor

    @api.depends('cost', 'last_published_cost')
    def _compute_cost_changed_recently(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            line.cost_changed_recently = not float_is_zero(
                line.cost - line.last_published_cost,
                precision_digits=price_rounding,
            )

    def _snapshot_published_cost(self):
        for line in self:
            line.last_published_cost = line.cost

