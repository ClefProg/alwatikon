# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import float_is_zero, float_round


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

    @api.onchange('display_name_id')
    def _onchange_display_name_id_load_prices(self):
        for line in self:
            if not line.display_name_id or not line.record_id:
                continue
            try:
                channel_map = line.record_id._resolve_channel_pricelists()
            except Exception:
                continue
                
            variants = line.display_name_id.variant_ids
            if not variants:
                continue
            seed_variant = variants[0]
            
            from .pricing_record import CHANNEL_PRICE_FIELD
            for channel, pricelist in channel_map.items():
                price = line.record_id._get_variant_fixed_price(pricelist, seed_variant)
                if price:
                    field_name = CHANNEL_PRICE_FIELD[channel]
                    setattr(line, field_name, price)
    cost = fields.Float(
        string='Cost (USD)',
        compute='_compute_cost',
        store=False,
        digits='Product Price',
    )
    wholesale_usd_price = fields.Float(
        string='W. USD Price',
        digits='Product Price',
    )
    retail_usd_price = fields.Float(
        string='R. USD Price',
        digits='Product Price',
    )
    wholesale_rate = fields.Float(
        related='record_id.wholesale_pricing_rate',
    )
    retail_rate = fields.Float(
        related='record_id.retail_pricing_rate',
    )
    wholesale_lyd_price = fields.Float(
        string='W. LYD Price',
        compute='_compute_prices',
        inverse='_inverse_wholesale_lyd_price',
        readonly=False,
        store=True,
        digits='Product Price',
    )
    retail_lyd_price = fields.Float(
        string='R. LYD Price',
        compute='_compute_prices',
        inverse='_inverse_retail_lyd_price',
        readonly=False,
        store=True,
        digits='Product Price',
    )
    wholesale_bank_price = fields.Float(
        string='W. Bank Price',
        compute='_compute_prices',
        inverse='_inverse_wholesale_bank_price',
        readonly=False,
        store=True,
        digits='Product Price',
    )
    retail_bank_price = fields.Float(
        string='R. Bank Price',
        compute='_compute_prices',
        inverse='_inverse_retail_bank_price',
        readonly=False,
        store=True,
        digits='Product Price',
    )
    retail_bnz_price = fields.Float(
        string='R. BNZ Price',
        compute='_compute_prices',
        inverse='_inverse_retail_bnz_price',
        readonly=False,
        store=True,
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

    @api.depends('display_name_id.average_cost', 'company_id')
    def _compute_cost(self):
        for line in self:
            cost = 0.0
            if line.display_name_id:
                cost = line.display_name_id.with_company(line.company_id).average_cost
            line.cost = cost
            # Only set default USD prices if they are empty to avoid overwriting manual edits during recomputes
            if not line.wholesale_usd_price:
                line.wholesale_usd_price = cost
            if not line.retail_usd_price:
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

            line.wholesale_lyd_price = float_round(wholesale_lyd, precision_digits=0)
            line.retail_lyd_price = float_round(retail_lyd, precision_digits=0)
            line.wholesale_bank_price = float_round(wholesale_lyd * bank_factor, precision_digits=0)
            line.retail_bank_price = float_round(retail_lyd * bank_factor, precision_digits=0)
            line.retail_bnz_price = float_round(retail_lyd * bnz_factor, precision_digits=0)

    def _inverse_wholesale_lyd_price(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            rate = line.record_id.wholesale_pricing_rate
            if rate:
                new_usd = line.wholesale_lyd_price / rate
                if not float_is_zero(line.wholesale_usd_price - new_usd, precision_digits=price_rounding):
                    line.wholesale_usd_price = new_usd

    def _inverse_retail_lyd_price(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            rate = line.record_id.retail_pricing_rate
            if rate:
                new_usd = line.retail_lyd_price / rate
                if not float_is_zero(line.retail_usd_price - new_usd, precision_digits=price_rounding):
                    line.retail_usd_price = new_usd

    def _inverse_wholesale_bank_price(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            rate = line.record_id.wholesale_pricing_rate
            factor = 1.0 + line.record_id.bank_markup
            if rate and factor:
                new_usd = line.wholesale_bank_price / (rate * factor)
                if not float_is_zero(line.wholesale_usd_price - new_usd, precision_digits=price_rounding):
                    line.wholesale_usd_price = new_usd

    def _inverse_retail_bank_price(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            rate = line.record_id.retail_pricing_rate
            factor = 1.0 + line.record_id.bank_markup
            if rate and factor:
                new_usd = line.retail_bank_price / (rate * factor)
                if not float_is_zero(line.retail_usd_price - new_usd, precision_digits=price_rounding):
                    line.retail_usd_price = new_usd

    def _inverse_retail_bnz_price(self):
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        for line in self:
            rate = line.record_id.retail_pricing_rate
            factor = 1.0 + line.record_id.eastern_region_markup
            if rate and factor:
                new_usd = line.retail_bnz_price / (rate * factor)
                if not float_is_zero(line.retail_usd_price - new_usd, precision_digits=price_rounding):
                    line.retail_usd_price = new_usd

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

