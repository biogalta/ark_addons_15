# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from functools import partial
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang

import math


class AccountTax(models.Model):
    _inherit = 'account.tax'
    _order = "name desc"

    is_eco_tax = fields.Boolean('Est un eco tax', default=False)
