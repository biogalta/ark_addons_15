# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from functools import partial

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang

import json


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def check_if_machine_exists(self):
        res = self.invoice_line_ids.filtered(lambda li: li.product_id.product_tmpl_id.categ_id.type == 'machine')
        return res

class InheritSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    default_code_product = fields.Char(related='product_id.default_code', string="Référence interne")
    current_invoiced_qty = fields.Float(string="Current qty invoiced", store=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.filtered(lambda l: not l.is_eco_tax).compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    tax_orders_ids = fields.One2many('sale.order.tax', 'order_id', string="TVA", compute='_amount_by_group')
    id_contact = fields.Integer(related='partner_id.id', string="Id")
    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group',
                                    help="type: [(name, amount, base, formated amount, formated base)]")
    amount_untaxe_eco = fields.Char(compute='_amount_by_group')
    commercial_id = fields.Many2one("res.partner", related="partner_id.commercial_id", string=_("Commercial"),
                                    store=True)
    promoter_id = fields.Many2one("res.partner", related="partner_id.promoter_id", string=_("Promoter"), store=True)


    def check_if_machine_exists(self):
        res = self.order_line.filtered(lambda li: li.product_id.product_tmpl_id.categ_id.type == 'machine')
        return res

    @api.depends('amount_tax')
    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.filtered(lambda l: not l.is_eco_tax).compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id,
                                                partner=order.partner_shipping_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax._origin.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
                    if tax.is_eco_tax:
                        res[group]['amount'] += tax['amount'] * line.product_uom_qty
                        res[group]['base'] += line.price_subtotal - (tax['amount'] * line.product_uom_qty)
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            list_tax_groups = []
            for l in res:
                if l[0].is_eco_tax == False:
                    list_tax_groups.append((
                        l[0].name, l[1]['amount'], l[1]['base'],
                        fmt(l[1]['amount']), fmt(l[1]['base']),
                        len(res), l[0].is_eco_tax, fmt(float(l[1]['amount']))
                    ))
            for l in res:
                if l[0].is_eco_tax == True:
                    list_tax_groups.append((
                        l[0].name, l[1]['amount'], l[1]['base'],
                        fmt(l[1]['amount']), fmt(l[1]['base']),
                        len(res), l[0].is_eco_tax, fmt(float(l[1]['amount']) * float(1.20))
                    ))
            order.amount_by_group = list_tax_groups
            list_ids = []
            amount_untaxe_eco_calcul = 0.0
            if order.amount_by_group:
                for line_amount in order.amount_by_group:
                    order_ref = self.env['sale.order.tax'].search(
                        [('order_id', '=', order.id), ('tax_name', '=', line_amount[0])])
                    for line_order in order_ref:
                        if line_order.tax_value != line_amount[1]:
                            line_order.unlink()
                    data = {
                        'tax_name': str(line_amount[0]) + " sur " + str(fmt(line_amount[2])),
                        'tax_value': str(fmt(round(float(line_amount[1]), 2))),
                        'is_eco_tax': line_amount[6]
                    }
                    ref = self.env['sale.order.tax'].create(data)
                    for line in ref:
                        list_ids.append(line.id)
                    if line_amount[6] == True:
                        amount_untaxe_eco_calcul = order.amount_untaxed + round(float(line_amount[1]), 2)
            order.amount_untaxe_eco = fmt(amount_untaxe_eco_calcul)

            if order.amount_by_group:
                for line_amount in order.amount_by_group:
                    if line_amount[6] == True:
                        data = {
                            'tax_name': "Taxe éco TTC sur " + str(fmt(line_amount[2])),
                            'tax_value': str(line_amount[7]),
                            'is_eco_tax': False
                        }
                        ref = self.env['sale.order.tax'].create(data)
                        for line in ref:
                            list_ids.append(line.id)

            order.tax_orders_ids = [(6, 0, list_ids)]

    @api.constrains('state', 'partner_id')
    def _check_state_sale(self):
        for sale in self:
            if sale.state == 'sale' and sale.partner_id.customer_rank == 0 and \
                sale.partner_id.is_promoter == False and sale.partner_id.is_commercial == False:
                raise UserError(_("You must modify this prospect in client to continue on order form"))

    def update_total(self):
        orders = self.search([])
        for order in orders:
            print(">>>>>>>>>>>>> traitement order:{}".format(order.name))
            order._amount_all()
            order._compute_tax_totals_json()
            print(">>>>>>>>>>>> Fin traitement order:{}".format(order.name))
        print("vita")

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id.filtered(lambda l: not l.is_eco_tax)._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            eco_tax = 0.0
            for line_tax in order.order_line:
                if len(line_tax.tax_id) >= 1:
                    for line_product_taxe in line_tax.tax_id:
                        if line_product_taxe.tax_group_id.is_eco_tax == True:
                            eco_tax += round((line_product_taxe.amount * line_tax.product_uom_qty), 2)
            amount_untaxed = amount_untaxed #Alice- eco_tax

            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax':  amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

class SaleOrderTax(models.Model):
    _name = 'sale.order.tax'

    tax_name = fields.Char('TVA')
    tax_value = fields.Char('Prix')
    order_id = fields.Many2one('sale.order')
    is_eco_tax = fields.Boolean('Is eco tax', default=False)
