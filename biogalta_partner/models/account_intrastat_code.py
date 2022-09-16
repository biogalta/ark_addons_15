# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.osv import expression


class InheritAccountIntrastatCode(models.Model):
    _inherit = 'account.intrastat.code'
    _translate = True

    name = fields.Char("Name")
    country_id = fields.Many2one('res.country', "Country",
                                 help="Restrict the applicability of code to a country.",
                                 domain="[('intrastat', '=', True)]")
    type = fields.Selection(string='Type', required=True,
        selection=[('commodity', _('Commodity')), ('transport', 'Transport'), ('transaction', 'Transaction'), ('region', _('Region'))],
        default='commodity',
        help=_('''Type of intrastat code used to filter codes by usage.
            * commodity: Code to be set on invoice lines for European Union statistical purposes.
            * transport: The active vehicle that moves the goods across the border.
            * transaction: A movement of goods.
            * region: A sub-part of the country.
        '''))