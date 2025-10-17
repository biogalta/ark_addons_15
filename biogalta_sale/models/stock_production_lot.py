# -*- coding: utf-8 -*-

from odoo import fields, models

class StockProcudtionLot(models.Model):
    _inherit = 'stock.lot'
    
    invoiced_lot = fields.Boolean("Invoiced lot")