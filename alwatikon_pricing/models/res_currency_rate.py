# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    dubai_rate_differential = fields.Float(
        string="Dubai Rate Differential",
        groups="account.group_account_manager",
        help="Manual differential over the inverse company rate. May be positive (markup) or negative (markdown)."
    )

    dubai_rate = fields.Float(
        string="Dubai Rate",
        compute="_compute_dubai_rate",
        store=True,
        groups="account.group_account_manager",
        help="Recomputes based on the inverse company rate and manual differential."
    )

    @api.depends('inverse_company_rate', 'dubai_rate_differential')
    def _compute_dubai_rate(self):
        for rate in self:
            rate.dubai_rate = rate.inverse_company_rate + rate.dubai_rate_differential
