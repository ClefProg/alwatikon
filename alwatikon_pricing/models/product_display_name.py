# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductDisplayName(models.Model):
    _name = 'product.display.name'
    _description = 'Product Display Name'

    name = fields.Char(required=True)
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

    def _compute_variant_count(self):
        for record in self:
            record.variant_count = len(record.variant_ids)

    def _compute_unassigned_variant_count(self):
        count = self.env['product.product'].search_count([('display_name_id', '=', False)])
        for record in self:
            record.unassigned_variant_count = count

    def action_unassigned_variants(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Unassigned Variants',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('display_name_id', '=', False)],
        }