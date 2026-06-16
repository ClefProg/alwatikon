# -*- coding: utf-8 -*-

from odoo import fields, models


class PricingRecord(models.Model):
    _name = 'pricing.record'
    _description = 'Pricing Record'

    name = fields.Char(required=True)
    line_ids = fields.One2many(
        'pricing.line',
        inverse_name='record_id',
        string='Lines',
    )


class PricingLine(models.Model):
    _name = 'pricing.line'
    _description = 'Pricing Line'

    record_id = fields.Many2one(
        'pricing.record',
        string='Pricing Record',
        required=True,
        ondelete='cascade',
    )
