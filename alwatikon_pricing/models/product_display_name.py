# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductDisplayName(models.Model):
    _name = 'product.display.name'
    _description = 'Product Display Name'

    name = fields.Char(required=True)
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Template',
        compute='_compute_product_tmpl_id',
    )
    variant_ids = fields.One2many(
        'product.product',
        inverse_name='display_name_id',
        string='Variants',
    )
    variant_count = fields.Integer(
        string='Variant Count',
        compute='_compute_variant_count',
    )
    unassigned_variant_count = fields.Integer(
        string='Unassigned Variants',
        compute='_compute_unassigned_variant_count',
    )
    usd_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_usd_currency_id',
    )
    average_cost = fields.Float(
        string='Average Cost (USD)',
        compute='_compute_average_cost',
    )

    def _compute_variant_count(self):
        for record in self:
            record.variant_count = len(record.variant_ids)

    @api.depends('variant_ids.product_tmpl_id')
    def _compute_product_tmpl_id(self):
        for record in self:
            record.product_tmpl_id = record.variant_ids[:1].product_tmpl_id

    def _compute_unassigned_variant_count(self):
        count = self.env['product.product'].search_count([('display_name_id', '=', False)])
        for record in self:
            record.unassigned_variant_count = count

    def _compute_usd_currency_id(self):
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            record.usd_currency_id = usd_currency and usd_currency.id or False

    @api.depends('variant_ids.current_usd_cost', 'variant_ids.qty_available')
    def _compute_average_cost(self):
        for record in self:
            cost = 0.0
            if record.variant_ids:
                total_qty = sum(record.variant_ids.mapped('qty_available'))
                if total_qty > 0:
                    weighted = sum(
                        variant.current_usd_cost * variant.qty_available
                        for variant in record.variant_ids
                    )
                    cost = weighted / total_qty
                else:
                    cost = sum(record.variant_ids.mapped('current_usd_cost')) / len(record.variant_ids)
            record.average_cost = cost

    def action_unassigned_variants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Unassigned Variants',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('display_name_id', '=', False)],
        }