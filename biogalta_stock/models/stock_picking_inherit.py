# -*- coding: utf-8 -*-

from odoo import api, fields, models

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPickingInherit, self).button_validate()
        return res
