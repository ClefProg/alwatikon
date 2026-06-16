# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_gain_account_id = fields.Many2one(
        'account.account',
        string='FX Gain Account',
    )
    currency_loss_account_id = fields.Many2one(
        'account.account',
        string='FX Loss Account',
    )
    fx_journal_id = fields.Many2one(
        'account.journal',
        string='FX Journal',
        domain="[('type', '=', 'general')]",
    )
    forecast_landed_pct = fields.Float(
        string='Forecast Landed %',
        default=0.0,
    )

