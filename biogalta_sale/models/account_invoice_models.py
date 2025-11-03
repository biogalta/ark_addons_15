# -*- coding: utf-8 -*-

from functools import partial
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
import json
import math


class InheritAccountInvoice(models.Model):
    _inherit = "account.move"

    tax_invoice_ids = fields.Many2many('tax.account.invoice', string="TVA", compute='_compute_amount')
    id_contact = fields.Integer(related='partner_id.id', string="Id")
    amount_untaxe_eco = fields.Char(compute='_compute_amount')
    commercial_id = fields.Many2one("res.partner", related="partner_id.commercial_id", string=_("Commercial"),
                                    store=True)
    promoter_id = fields.Many2one("res.partner", related="partner_id.promoter_id", string=_("Promoter"), store=True)
    skip_count = fields.Boolean(string="skip_count", default=False, store=True)

    amount_by_group = fields.Binary(string="Tax amount by group", compute='_compute_amount',
                                    help="type: [(name, amount, base, formated amount, formated base)]")
    subtotal_eco = fields.Char(string='Sous-total HT dont éco-contribution', readonly=True, compute="_compute_subtotal_eco")

    def _compute_subtotal_eco(self):
        for move in self:
            sub = 0
            currency = move.currency_id or move.company_id.currency_id
            fmt = partial(formatLang, move.with_context(lang=move.partner_id.lang).env, currency_obj=currency)
            for line in move.invoice_line_ids:
                sub += line.price_subtotal_uneco
            move.subtotal_eco = str(fmt(round(float(sub), 2)))

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.origin_payment_id.is_matched',  
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.origin_payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        'state')
    def _compute_amount(self):
        res = super(InheritAccountInvoice, self)._compute_amount()
        for invoice in self:
            currency = invoice.currency_id or invoice.company_id.currency_id
            fmt = partial(formatLang, invoice.with_context(lang=invoice.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in invoice.invoice_line_ids:
                taxes = line.tax_ids.filtered(lambda l: not l.is_eco_tax)._origin.compute_all(
                    (line.price_unit * (1 - (line.discount / 100.0))),
                    quantity=line.quantity,
                    product=line.product_id,
                    partner=invoice.partner_shipping_id)['taxes']
                for tax in line.tax_ids:
                    group = tax.tax_group_id
                    res.setdefault(group, {'base': 0.0, 'amount': 0.0})
                    for t in taxes:
                        if t['id'] == tax._origin.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
                    if tax.is_eco_tax:
                        res[group]['amount'] += tax['amount'] * line.quantity
                        res[group]['base'] += line.price_subtotal
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            list_tax_groups = []
            for r in res:
                if r[0].is_eco_tax == False:
                    list_tax_groups.append((
                        r[0].name, r[1]['amount'], r[1]['base'],
                        fmt(r[1]['amount']), fmt(r[1]['base']),
                        len(res), r[0].is_eco_tax, fmt(float(r[1]['amount']) * float(1.20))
                    ))
            for r in res:
                if r[0].is_eco_tax == True:
                    list_tax_groups.append((
                        r[0].name, r[1]['amount'], r[1]['base'],
                        fmt(r[1]['amount']), fmt(r[1]['base']),
                        len(res), r[0].is_eco_tax, fmt(float(r[1]['amount']) * float(1.20))
                    ))
            invoice.amount_by_group = list_tax_groups
            list_ids = []
            amount_untaxe_eco_calcul = 0.0
            if invoice.amount_by_group:
                for line_amount in invoice.amount_by_group:
                    invoice_ref = self.env['tax.account.invoice'].search(
                        [('invoice_id', '=', invoice.id), ('tax_name', '=', line_amount[0])])
                    for line_invoice in invoice_ref:
                        if line_invoice.tax_value != line_amount[1]:
                            line_invoice.unlink()
                    data = {
                        'tax_name': str(line_amount[0]) + " sur " + str(fmt(line_amount[2])),
                        'tax_value': str(fmt(round(float(line_amount[1]), 2))),
                        'is_eco_tax': line_amount[6]
                    }
                    ref = self.env['tax.account.invoice'].create(data)
                    for line in ref:
                        list_ids.append(line.id)
                    if line_amount[6] == True:
                        amount_untaxe_eco_calcul = invoice.amount_untaxed + round(float(line_amount[1]), 2)
            invoice.amount_untaxe_eco = fmt(amount_untaxe_eco_calcul)

            if invoice.amount_by_group:
                for line_amount in invoice.amount_by_group:
                    if line_amount[6] == True:
                        data = {
                            'tax_name': "Taxe éco TTC sur " + str(fmt(line_amount[2])),
                            'tax_value': str(line_amount[7]),
                            'is_eco_tax': False
                        }
                        ref = self.env['tax.account.invoice'].create(data)
                        for line in ref:
                            list_ids.append(line.id)

            invoice.tax_invoice_ids = [(6, 0, list_ids)]

    def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
        """ Compute the dynamic tax lines of the journal entry.

        :param recompute_tax_base_amount: Flag forcing only the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            ''' Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by '_get_tax_grouping_key_from_tax_line' or '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            return base_line.tax_ids.filtered(lambda l : not l.is_eco_tax)._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )
        def _compute_base_line_taxes_2(base_line):
            ''' Compute taxes amounts both in company currency / foreign currency as the ratio between
            amount_currency & balance could not be the same as the expected currency rate.
            The 'amount_currency' value will be set on compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                price_unit_wo_discount = sign * base_line.price_unit * (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            return base_line.tax_ids.filtered(lambda l : l.is_eco_tax)._origin.with_context(force_sign=move._get_tax_force_sign()).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist, we only need one
                # to modify it; we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)
            compute_all_vals_2 = _compute_base_line_taxes_2(line)
            compute_all_res = compute_all_vals['taxes'] + compute_all_vals_2['taxes']

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or [(5, 0, 0)]

            for tax_vals in compute_all_res:
                grouping_dict = self._get_tax_grouping_key_from_base_line(line, tax_vals)
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(grouping_key, {
                    'tax_line': None,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                })
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += self._get_base_amount_to_display(tax_vals['base'], tax_repartition_line, tax_vals['group'])
                taxes_map_entry['grouping_dict'] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            currency = self.env['res.currency'].browse(taxes_map_entry['grouping_dict']['currency_id'])

            # Don't create tax lines with zero balance.
            if currency.is_zero(taxes_map_entry['amount']):
                if taxes_map_entry['tax_line'] and not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = currency._convert(taxes_map_entry['tax_base_amount'], self.company_currency_id, self.company_id, self.date or fields.Date.context_today(self))

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = tax_base_amount
                continue

            balance = currency._convert(
                taxes_map_entry['amount'],
                self.company_currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                if tax_rep_lines_to_recompute and taxes_map_entry['tax_line'].tax_repartition_line_id not in tax_rep_lines_to_recompute:
                    continue

                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                tax_repartition_line_id = taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env['account.tax.repartition.line'].browse(tax_repartition_line_id)

                if tax_rep_lines_to_recompute and tax_repartition_line not in tax_rep_lines_to_recompute:
                    continue

                tax = tax_repartition_line.invoice_tax_id or tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method({
                    **to_write_on_line,
                    'name': tax.name,
                    'move_id': self.id,
                    'company_id': self.company_id.id,
                    'company_currency_id': self.company_currency_id.id,
                    'tax_base_amount': tax_base_amount,
                    'exclude_from_invoice_tab': True,
                    **taxes_map_entry['grouping_dict'],
                })

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(taxes_map_entry['tax_line']._get_fields_onchange_balance(force_computation=True))

    def action_post(self):
        res = super(InheritAccountInvoice, self).action_post()
        #update serial number invoiced status
        StockProductionLot = self.env['stock.lot']
        for line in self.invoice_line_ids:
            if line.serial_num:
                lot_id = StockProductionLot.search([('name','=',line.serial_num)])
                if lot_id:
                    lot_id.invoiced_lot = True
        return res

class InheritInvoiceTax(models.Model):
    _name = 'tax.account.invoice'

    tax_name = fields.Char('TVA')
    tax_value = fields.Char('Prix')
    invoice_id = fields.Many2one('account.move')
    is_eco_tax = fields.Boolean('Is eco tax', default=False)


class InheritAccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    default_code_product = fields.Char(related='product_id.default_code', string="Référence interne")
    serial_num = fields.Char(string="Serial Number", store=True)
    price_subtotal_uneco = fields.Monetary(string='Montant HT dont éco-contribution', readonly=True, compute="_compute_sub_eco",
                                     currency_field='currency_id')

    @api.depends('price_subtotal')
    def _compute_sub_eco(self):
        for line in self:
            eco = 0
            for tax in line.tax_ids.filtered(lambda l : l.is_eco_tax):
                eco += tax.amount
            line.price_subtotal_uneco = line.price_subtotal + eco * line.quantity

    @api.model_create_multi
    def create(self, vals):
        res = super(InheritAccountInvoiceLine, self).create(vals)
        for rec in res:
            rec._compute_serial()
        return res

    def _compute_serial(self):
        """
        Get the serial number of the article
            Get all the composant of the product in stock_move_lines if they have serial.
            If it is a simple product => not write his default_code
        :return:
        """
        for rec in self:
            origin = rec.move_id.invoice_origin
            lot_retournes = self._get_lot_retours(origin, rec.product_id)
            lot_livres = self._get_lot_livres(origin, rec.product_id)
            lot_ = []
            for l in lot_livres:
                if l not in lot_retournes and l:
                    lot_.append(l)
            new_lot = self._check_facturation(lot_)
            rec.serial_num = ' - '.join(new_lot)

    def _check_facturation(self, lot_):
        StockProductionLot = self.env['stock.lot']
        for lot in lot_:
            lot_exists = StockProductionLot.search([('name','=',lot)], limit=1)
            if lot_exists and lot_exists.invoiced_lot:
                lot_.remove(lot)
        return lot_

    def _get_lot_retours(self, origin, product):
        liste_retours = []
        lots_retours = self.env['stock.picking'].sudo().search(
            ['&', ('group_id.name', '=', origin), ('origin', 'ilike', 'Retour%')])
        ids_product_on_bom = []
        boms = self.env['mrp.bom'].sudo().search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)
        if lots_retours:
            for retour in lots_retours:
                if retour.move_line_ids:
                    for lotretour in retour.move_line_ids:
                        if boms:
                            ids_product_on_bom = [p.product_id.id for p in boms.bom_line_ids]
                        if lotretour.lot_id.name not in liste_retours and (
                                lotretour.product_id.id == product.id or lotretour.product_id.id in ids_product_on_bom):
                            liste_retours.append(lotretour.lot_id.name)
        return liste_retours

    def _get_lot_livres(self, origin, product):
        liste_livres = []
        all_picks = self.env['stock.picking'].search([('origin', '=', origin)])
        ids_product_on_bom = []
        boms = self.env['mrp.bom'].sudo().search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)
        if all_picks:
            for picks in all_picks:
                if picks.move_line_ids:
                    for p in picks.move_line_ids:
                        if boms:
                            ids_product_on_bom = [p.product_id.id for p in boms.bom_line_ids]
                        if p.lot_id.name not in liste_livres and (
                                p.product_id.id == product.id or p.product_id.id in ids_product_on_bom):
                            liste_livres.append(p.lot_id.name)
        return liste_livres

    def _get_last_lot(self, origin, product):
        liste_lot = []
        last_pick = self.env['stock.picking'].search([('origin', '=', origin), ('state', '=', 'done')],
                                                     order="create_date desc")
        ids_product_on_bom = []
        boms = self.env['mrp.bom'].sudo().search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)], limit=1)
        if last_pick:
            for picks in last_pick:
                for p in picks.move_line_ids:
                    if boms:
                        ids_product_on_bom = [p.product_id.id for p in boms.bom_line_ids]
                    if p.lot_id.name and p.lot_id.name not in liste_lot and (
                            p.product_id.id == product.id or p.product_id.id in ids_product_on_bom):
                        liste_lot.append(p.lot_id.name)
        return liste_lot
