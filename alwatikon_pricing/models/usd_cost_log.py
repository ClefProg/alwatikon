# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.exceptions import UserError


class UsdCostLog(models.Model):
    _name = 'usd.cost.log'
    _description = 'USD Cost Change Log'
    _order = 'create_date desc, id desc'
    _rec_name = 'product_id'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        index=True,
        ondelete='restrict',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        readonly=True,
    )
    type = fields.Selection(
        selection=[('purchase', 'Purchase')],
        string='Type',
        required=True,
        default='purchase',
        readonly=True,
    )
    old_cost = fields.Float(
        string='Old Cost (USD)',
        readonly=True,
    )
    new_cost = fields.Float(
        string='New Cost (USD)',
        readonly=True,
    )
    old_qty = fields.Float(
        string='On-hand Before',
        readonly=True,
    )
    new_qty = fields.Float(
        string='On-hand After',
        readonly=True,
    )
    reference = fields.Char(
        string='Reference',
        readonly=True,
        help='Purchase order number when the change originated from a receipt.',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Vendor',
        readonly=True,
    )

    def write(self, vals):
        raise UserError(_('USD cost log entries are read-only and cannot be modified.'))

    def unlink(self):
        raise UserError(_('USD cost log entries are read-only and cannot be deleted.'))
