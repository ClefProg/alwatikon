# -*- coding: utf-8 -*-

from odoo import fields, models


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
