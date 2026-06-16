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
from email.policy import default

from odoo import api, fields, models, _,api


class PosPayment(models.Model):
    _inherit = 'pos.payment'

    payment_currency = fields.Char(string='Payment Currency',)
    currency_amount = fields.Float(string='Exchanged Amount')
    payment_symbol = fields.Char(string='Currency Amount')
    multi_currency = fields.Boolean(string='Multi Currency', default=False)






