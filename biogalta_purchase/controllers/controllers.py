# -*- coding: utf-8 -*-
from odoo import http

# class BiogaltaPurchase(http.Controller):
#     @http.route('/biogalta_purchase/biogalta_purchase/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biogalta_purchase/biogalta_purchase/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biogalta_purchase.listing', {
#             'root': '/biogalta_purchase/biogalta_purchase',
#             'objects': http.request.env['biogalta_purchase.biogalta_purchase'].search([]),
#         })

#     @http.route('/biogalta_purchase/biogalta_purchase/objects/<model("biogalta_purchase.biogalta_purchase"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biogalta_purchase.object', {
#             'object': obj
#         })