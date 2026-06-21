# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_gain_account_id = fields.Many2one(
        'account.account',
        config_parameter='alwatikon_pricing.currency_gain_account_id',
        string='FX Gain Account',
    )
    currency_loss_account_id = fields.Many2one(
        'account.account',
        config_parameter='alwatikon_pricing.currency_loss_account_id',
        string='FX Loss Account',
    )
    fx_journal_id = fields.Many2one(
        'account.journal',
        config_parameter='alwatikon_pricing.fx_journal_id',
        string='FX Journal',
        domain="[('type', '=', 'general')]",
    )
    forecast_landed_pct = fields.Float(
        string='Forecast Landed %',
        config_parameter='alwatikon_pricing.forecast_landed_pct',
        default=0.0,
    )

