# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api

class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_sh_enable_payment_in_pricelist = fields.Boolean(
        related="pos_config_id.sh_enable_payment_in_pricelist", readonly=False)
    pos_sh_allow_to_change_currency_rate = fields.Boolean(
        related="pos_config_id.sh_allow_to_change_currency_rate", readonly=False)
