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

from odoo import api, fields, models, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_multi_currency = fields.Boolean(
        string="Enable Multi Currency",
        default=False
    )

    currencies_ids = fields.Many2many(
        'res.currency',
        string="Currencies",
        compute=False,
    )
