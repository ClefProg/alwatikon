# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import models,fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    sh_currency_id = fields.Many2one('res.currency','sh_currency_id')

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """
    #     Overrides the create method to set the product's list price (Sales Price)
    #     as the unit price for each order line before the order is created.
    #     """

    #     for vals in vals_list:
    #         session = self.env["pos.session"].browse(vals.get("session_id"))
    #         pos_config = session.config_id if session else False
    #         if pos_config and pos_config.sh_enable_payment_in_pricelist and pos_config.pricelist_id != vals.get('pricelist_id'):
    #             vals['pricelist_id'] = pos_config.pricelist_id.id
    #     return super(PosOrder, self).create(vals_list)
