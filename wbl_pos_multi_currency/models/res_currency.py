# -*- coding: utf-8 -*-
#
#################################################################################
# Author      : Weblytic Labs Pvt. Ltd. (<https://store.weblyticlabs.com/>)
# Copyright(c): 2023-Present Weblytic Labs Pvt. Ltd.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
##################################################################################
from odoo import models, api
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def get_config_currencies(self, config_id):
        config = self.env['pos.config'].browse(config_id)
        if not config.exists():
            return []

        currencies = config.currencies_ids
        currency = currencies.read([
            'id',
            'name',
            'rate',
            'symbol',
            'position',
            'rounding',
            'decimal_places',
        ])
        return currency
