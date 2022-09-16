# -*- coding: utf-8 -*-
from odoo import fields, models

from odoo.exceptions import ValidationError


class AccountTaxCarryoverLine(models.Model):
    _inherit = 'account.tax.carryover.line'

    tax_report_country_id = fields.Many2one(
    	string="Country", comodel_name='res.country', required=True, 
    	default=lambda x: x.env.company.country_id.id, help="Country for which this report is available.")