# -*- coding: utf-8 -*-

from odoo import fields, models


class UsdCostLog(models.Model):
    _name = 'usd.cost.log'
    _description = 'USD Cost Log'

    name = fields.Char(required=True)