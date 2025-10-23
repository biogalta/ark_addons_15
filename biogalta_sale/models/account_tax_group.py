# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError

import math
import logging


TYPE_TAX_USE = [
    ('sale', 'Sales'),
    ('purchase', 'Purchases'),
    ('none', 'None'),
]


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'
    _description = 'Tax Group'
    _order = 'sequence asc'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    property_tax_payable_account_id = fields.Many2one('account.account', company_dependent=True, string='Tax current account (payable)')
    property_tax_receivable_account_id = fields.Many2one('account.account', company_dependent=True, string='Tax current account (receivable)')
    property_advance_tax_payment_account_id = fields.Many2one('account.account', company_dependent=True, string='Advance Tax payment account')
    country_id = fields.Many2one(string="Country", comodel_name='res.country', help="The country for which this tax group is applicable.")
    preceding_subtotal = fields.Char(
        string="Preceding Subtotal",
        help="If set, this value will be used on documents as the label of a subtotal excluding this tax group before displaying it. " \
             "If not set, the tax group will be displayed after the 'Untaxed amount' subtotal.",
    )
    is_eco_tax = fields.Boolean('Is eco tax', default=False)    
    
    @api.model
    def _check_misconfigured_tax_groups(self, company, countries):
        """ Searches the tax groups used on the taxes from company in countries that don't have
        at least a tax payable account, a tax receivable account or an advance tax payment account.

        :return: A boolean telling whether or not there are misconfigured groups for any
                 of these countries, in this company
        """

        # This cannot be refactored to check for misconfigured groups instead
        # because of an ORM limitation with search on property fields:
        # searching on property = False also returns the properties using the default value,
        # even if it's non-empty.
        # (introduced here https://github.com/odoo/odoo/pull/6044)
        all_configured_groups_ids = self.with_company(company)._search([
            ('property_tax_payable_account_id', '!=', False),
            ('property_tax_receivable_account_id', '!=', False),
        ])

        return bool(self.env['account.tax'].search([
            ('company_id', '=', company.id),
            ('tax_group_id', 'not in', all_configured_groups_ids),
            ('country_id', 'in', countries.ids),
        ], limit=1))