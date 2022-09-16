# -*- coding: utf-8 -*-

from odoo import fields, models

class product_categ(models.Model):
    _inherit = 'product.category'
    
    type = fields.Selection([('machine','Machine')],string="Type")