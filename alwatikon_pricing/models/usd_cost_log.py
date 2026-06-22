# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
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

    @api.model_create_multi
    def create(self, vals_list):
        logs = super().create(vals_list)
        logs._alw_sync_pricing_drafts()
        return logs

    def _get_pricing_manager_uid(self):
        raw = self.env['ir.config_parameter'].sudo().get_param(
            'alwatikon_pricing.pricing_manager_uid',
        )
        if not raw or raw in ('False', '0'):
            raise UserError(_('Pricing manager is not configured in the settings.'))
        try:
            uid = int(raw)
        except ValueError:
            raise UserError(_(
                'Pricing manager setting is invalid. '
                'Open Settings → Alwatikon Pricing and select a Pricing Manager.'
            ))
        if not uid or not self.env['res.users'].sudo().browse(uid).exists():
            raise UserError(_('Pricing manager is not configured in the settings.'))
        return uid

    def _alw_sync_pricing_drafts(self):
        """Upsert open draft pricing records when a display name's USD cost changes."""
        PricingRecord = self.env['pricing.record'].sudo()
        PricingRecordLine = self.env['pricing.record.line'].sudo()
        by_company = {}
        for log in self:
            display_name = log.product_id.display_name_id
            if display_name:
                by_company.setdefault(log.company_id, set()).add(display_name.id)

        for company, display_name_ids in by_company.items():
            draft = PricingRecord.search(
                [('state', '=', 'draft'), ('company_id', '=', company.id)],
                order='id desc',
                limit=1,
            )
            if not draft:
                draft = PricingRecord.create({
                    'company_id': company.id,
                })

            existing_display_names = set(
                draft.line_ids.mapped('display_name_id').ids
            )
            new_display_names = [
                dn_id for dn_id in display_name_ids if dn_id not in existing_display_names
            ]
            if not new_display_names:
                continue

            PricingRecordLine.create([
                {'record_id': draft.id, 'display_name_id': dn_id}
                for dn_id in new_display_names
            ])
            draft.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=fields.Date.context_today(draft),
                summary=_('Update & publish prices (cost changed)'),
                user_id=self._get_pricing_manager_uid(),
            )

    def write(self, vals):
        raise UserError(_('USD cost log entries are read-only and cannot be modified.'))

    def unlink(self):
        raise UserError(_('USD cost log entries are read-only and cannot be deleted.'))
