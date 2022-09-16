# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, pycompat

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_price_history_ids = fields.One2many('product.price.history', 'product_id')
    latest_inventory_date = fields.Datetime('Latest Inventory Date')
    price_used = fields.Float(
        'Price used', compute='_compute_stock_value')

    def write(self, values):
        res = super(ProductProduct, self).write(values)
        if 'standard_price' in values:
            self._set_standard_price(values['standard_price'])
        if len(self.product_price_history_ids) > 0:
            for item in self.product_price_history_ids:
                if item.cost == 0:
                    item.write({'cost':self.standard_price})
        else:
            self.env['product.price.history'].sudo().create({'company_id': self.env.user.company_id.id,'product_id':self.id,'datetime':self.create_date, 'cost': self.standard_price})
            if self.latest_inventory_date:
                self.env['product.price.history'].sudo().create({'company_id': self.env.user.company_id.id,'product_id':self.id,'datetime':self.latest_inventory_date, 'cost': self.standard_price})
        return res

    def _set_standard_price(self, value):
        ''' Store the standard price change in order to be able to retrieve the cost of a product for a given date'''
        PriceHistory = self.env['product.price.history']
        for product in self:
            PriceHistory.create({
                'product_id': product.id,
                'cost': value,
                'company_id': self._context.get('force_company', self.env.user.company_id.id),
            })


class ProductPriceHistory(models.Model):
    """ Keep track of the ``product.template`` standard prices as they are changed. """
    _name = 'product.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'
    _description = 'Product Price List History'

    company_id = fields.Many2one('res.company', string='Company', required=True)
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade', required=True)
    datetime = fields.Datetime('Date', default=fields.Datetime.now)
    cost = fields.Float('Cost', digits=dp.get_precision('Product Price'))

    @api.model
    def _get_initial_cost(self):
        initial_cost = 0.0
        for rec in self:
            if rec.initial_cost != 0:
                initial_cost = rec.initial_cost
            else:
                initial_cost = rec.product_id.standard_price
        return initial_cost

    initial_cost = fields.Float('Initial Cost', default=_get_initial_cost)
