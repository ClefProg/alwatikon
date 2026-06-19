# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

PRICING_CHANNELS = (
    'wholesale_usd',
    'wholesale_lyd',
    'wholesale_bank',
    'retail_usd',
    'retail_lyd',
    'retail_bank',
    'retail_bnz',
)
CHANNEL_PRICE_FIELD = {
    'wholesale_usd': 'wholesale_usd_price',
    'wholesale_lyd': 'wholesale_lyd_price',
    'wholesale_bank': 'wholesale_bank_price',
    'retail_usd': 'retail_usd_price',
    'retail_lyd': 'retail_lyd_price',
    'retail_bank': 'retail_bank_price',
    'retail_bnz': 'retail_bnz_price',
}


class PricingRecord(models.Model):
    _name = 'pricing.record'
    _description = 'Pricing Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    name = fields.Char(required=True, copy=False)
    publish_date = fields.Date(readonly=True, copy=False)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    wholesale_pricing_rate = fields.Float(
        string='Wholesale Pricing Rate',
        digits=(16, 5),
        default=0.0,
        help='USD to LYD forecast rate for the wholesale channel.',
    )
    retail_pricing_rate = fields.Float(
        string='Retail Pricing Rate',
        digits=(16, 5),
        default=0.0,
        help='USD to LYD forecast rate for the retail channel.',
    )
    bank_markup = fields.Float(
        string='Bank Markup',
        default=0.0,
        help='Fraction applied to LYD prices for bank channels (e.g. 0.06 = 6%).',
    )
    eastern_region_markup = fields.Float(
        string='Eastern Region Markup',
        default=0.06,
        help='Fraction applied to retail LYD for the BNZ channel (e.g. 0.06 = 6%).',
    )
    shipping = fields.Float(
        string='Shipping',
        help='Forecast landed cost input (informational).',
    )
    cfr_cost = fields.Float(
        string='CFR Cost',
        help='Forecast landed cost input (informational).',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('published', 'Published'),
        ],
        string='Status',
        default='draft',
        required=True,
        copy=False,
        tracking=True,
    )
    version = fields.Integer(
        string='Version',
        default=0,
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        'pricing.record.line',
        'record_id',
        string='Lines',
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        icp = self.env['ir.config_parameter'].sudo()
        param_defaults = {
            'wholesale_pricing_rate': (
                'alwatikon_pricing.default_wholesale_pricing_rate', '0',
            ),
            'retail_pricing_rate': (
                'alwatikon_pricing.default_retail_pricing_rate', '0',
            ),
            'bank_markup': (
                'alwatikon_pricing.default_bank_markup', '0',
            ),
            'eastern_region_markup': (
                'alwatikon_pricing.default_eastern_region_markup', '0.06',
            ),
        }
        for field, (param_key, fallback) in param_defaults.items():
            if field in fields_list and field not in res:
                res[field] = float(icp.get_param(param_key, fallback))
        return res

    def _channel_selection_labels(self):
        return dict(
            self.env['product.pricelist']._fields['pricing_channel'].selection
        )

    def _resolve_channel_pricelists(self, channels=None):
        """Map each pricing channel to exactly one pricelist for this record's company."""
        self.ensure_one()
        channels = channels or PRICING_CHANNELS
        labels = self._channel_selection_labels()
        domain = [
            ('pricing_channel', 'in', list(channels)),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', self.company_id.id),
        ]
        pricelists = self.env['product.pricelist'].search(domain)
        channel_map = {}
        for pricelist in pricelists:
            channel = pricelist.pricing_channel
            if not channel:
                continue
            if channel in channel_map:
                label = labels.get(channel, channel)
                raise UserError(_(
                    'Multiple pricelists are configured for pricing channel "%(channel)s". '
                    'Each channel must map to exactly one pricelist.',
                    channel=label,
                ))
            channel_map[channel] = pricelist

        missing = [ch for ch in channels if ch not in channel_map]
        if missing:
            missing_labels = ', '.join(labels.get(ch, ch) for ch in missing)
            raise UserError(_(
                'Cannot proceed: the following pricing channels have no pricelist '
                'configured for company "%(company)s": %(channels)s. '
                'Set Pricing Channel on each of the seven pricelists first.',
                company=self.company_id.display_name,
                channels=missing_labels,
            ))
        return channel_map

    def _get_variant_fixed_price(self, pricelist, variant):
        items = self.env['product.pricelist.item'].search([
            ('pricelist_id', '=', pricelist.id),
            ('applied_on', '=', '0_product_variant'),
            ('product_id', '=', variant.id),
        ], order='min_quantity desc, id desc')
        return items[:1].fixed_price if items else 0.0

    def _get_instock_variant_line_map(self):
        self.ensure_one()
        lines_by_variant = {}
        for line in self.line_ids:
            if not line.display_name_id:
                continue
            variants = line.display_name_id.variant_ids.with_company(self.company_id)
            for variant in variants:
                if variant.qty_available >= 1:
                    lines_by_variant[variant.id] = line
        return lines_by_variant

    def action_update(self):
        """Re-read wholesale/retail USD list prices onto every line from pricelists."""
        for record in self:
            channel_map = record._resolve_channel_pricelists(
                channels=('wholesale_usd', 'retail_usd'),
            )
            wholesale_pl = channel_map['wholesale_usd']
            retail_pl = channel_map['retail_usd']
            for line in record.line_ids:
                variants = line.display_name_id.variant_ids
                if not variants:
                    continue
                seed_variant = variants[0]
                line.write({
                    'wholesale_usd_price': record._get_variant_fixed_price(
                        wholesale_pl, seed_variant,
                    ),
                    'retail_usd_price': record._get_variant_fixed_price(
                        retail_pl, seed_variant,
                    ),
                })
        return True

    def action_publish(self):
        for record in self:
            record._action_publish_single()
        return True

    def _action_publish_single(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('Cannot publish a pricing record without lines.'))

        channel_map = self._resolve_channel_pricelists()
        lines_by_variant = self._get_instock_variant_line_map()
        price_rounding = self.env['decimal.precision'].precision_get('Product Price')
        PricelistItem = self.env['product.pricelist.item']

        for channel, pricelist in channel_map.items():
            field_name = CHANNEL_PRICE_FIELD[channel]
            variant_ids = list(lines_by_variant.keys())
            if not variant_ids:
                continue

            items = PricelistItem.search([
                ('pricelist_id', '=', pricelist.id),
                ('applied_on', '=', '0_product_variant'),
                ('product_id', 'in', variant_ids),
            ])
            items_by_product = defaultdict(list)
            for item in items:
                items_by_product[item.product_id.id].append(item)

            to_create = []
            for variant_id, line in lines_by_variant.items():
                price = line[field_name]
                if price < 0 or float_is_zero(price, precision_digits=price_rounding):
                    continue
                existing = items_by_product.get(variant_id, [])
                if existing:
                    for item in existing:
                        item.fixed_price = price
                else:
                    to_create.append({
                        'pricelist_id': pricelist.id,
                        'applied_on': '0_product_variant',
                        'compute_price': 'fixed',
                        'fixed_price': price,
                        'min_quantity': 0,
                        'product_id': variant_id,
                    })
            if to_create:
                PricelistItem.create(to_create)

        self.line_ids._snapshot_published_cost()
        new_version = self.version + 1
        self.write({
            'state': 'published',
            'version': new_version,
            'publish_date': fields.Date.context_today(self),
        })
        self.message_post(
            body=_('Pricing record published (version %s).', new_version),
        )
