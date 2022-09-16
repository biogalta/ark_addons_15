# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, _,api


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    default_code_product = fields.Char(related='product_id.default_code', string="Référence interne")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    commercial_id = fields.Many2one("res.partner", related="partner_id.commercial_id", string=_("Commercial"),
                                    store=True)
    promoter_id = fields.Many2one("res.partner", related="partner_id.promoter_id", string=_("Promoter"), store=True)