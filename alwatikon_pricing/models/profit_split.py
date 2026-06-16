# -*- coding: utf-8 -*-

from odoo import fields, models


class ProfitSplit(models.Model):
    _name = 'profit.split'
    _description = 'Profit Split'

    name = fields.Char(required=True)