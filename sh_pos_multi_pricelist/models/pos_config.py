# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_enable_payment_in_pricelist = fields.Boolean(string="Allow Payment In Pricelist Currency")
    sh_allow_to_change_currency_rate = fields.Boolean(string="Allow to Change Currency Rate")

    @api.constrains('pricelist_id', 'use_pricelist', 'available_pricelist_ids', 'journal_id', 'invoice_journal_id', 'payment_method_ids')
    def _check_currencies(self):
        for config in self:
            if config.use_pricelist and config.pricelist_id and config.pricelist_id not in config.available_pricelist_ids:
                raise ValidationError(_("The default pricelist must be included in the available pricelists."))

            # Check if the config's payment methods are compatible with its currency
            for pm in config.payment_method_ids:
                if pm.journal_id and pm.journal_id.currency_id and pm.journal_id.currency_id != config.currency_id:
                    raise ValidationError(_("All payment methods must be in the same currency as the Sales Journal or the company currency if that is not set."))

            # if (not config.sh_enable_payment_in_pricelist) and config.use_pricelist and config.pricelist_id and any(config.available_pricelist_ids.mapped(lambda pricelist: pricelist.currency_id != config.currency_id)):
            #     raise ValidationError(_("All available pricelists must be in the same currency as the company or"
            #                             " as the Sales Journal set on this point of sale if you use"
            #                             " the Accounting application."))
            if config.invoice_journal_id.currency_id and config.invoice_journal_id.currency_id != config.currency_id:
                raise ValidationError(_("The invoice journal must be in the same currency as the Sales Journal or the company currency if that is not set."))
