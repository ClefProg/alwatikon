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