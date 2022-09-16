# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('move_id.line_ids', 'move_id.line_ids.tax_line_id', 'move_id.line_ids.debit',
                 'move_id.line_ids.credit')
    def _compute_tax_base_amount(self):
        super(AccountMoveLine, self)._compute_tax_base_amount()
        for move_line in self:
            if move_line.tax_line_id:
                base_lines = move_line.move_id.line_ids.filtered(lambda line: move_line.tax_line_id in line.tax_ids)
                for line in base_lines:
                    if any(tax.price_include and tax.tax_group_id.is_eco_tax for tax in line.tax_ids):
                        for tax in line.tax_ids.filtered(lambda tx: tx.tax_group_id.is_eco_tax and tx.price_include):
                            move_line.tax_base_amount += abs(sum(move_line.move_id.line_ids.filtered(lambda line: line.tax_line_id == tax) \
                                                         .mapped('balance'))) or 0
            else:
                move_line.tax_base_amount = 0
