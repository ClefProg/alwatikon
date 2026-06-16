# Copyright (C) Softhealer Technologies.
# Part of Softhealer Technologies.

from odoo import models, api
from odoo.fields import Domain


class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_pricelist(self):
        result = super(PosSessionInherit,
                       self)._loader_params_product_pricelist()
        result['search_params']['fields'].append('currency_id')
        return result

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        loaded_data['currency_by_id'] = {
            cur['id']: cur for cur in self.env['res.currency'].search_read([('active', '=', True)])}
        if self.order_ids:
            order_amount_by_currency = {}
            for each_order_id in self.order_ids:
                if each_order_id.sh_currency_id:
                    if order_amount_by_currency.get(each_order_id.sh_currency_id.id):
                        order_amount_by_currency[each_order_id.sh_currency_id.id] = order_amount_by_currency[
                            each_order_id.sh_currency_id.id] + each_order_id.amount_total
                    else:
                        order_amount_by_currency[each_order_id.sh_currency_id.id] = each_order_id.amount_total
            loaded_data['amount_by_currency'] = order_amount_by_currency


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ['currency_id']


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _load_pos_data_domain(self, data, config):
        domain = super()._load_pos_data_domain(data, config)
        domain = Domain.OR([domain, [('active', '=', True)]])
        return domain
