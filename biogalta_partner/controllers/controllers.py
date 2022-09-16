# -*- coding: utf-8 -*-
from odoo import http

# class BiogaltaPartner(http.Controller):
#     @http.route('/biogalta_partner/biogalta_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/biogalta_partner/biogalta_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('biogalta_partner.listing', {
#             'root': '/biogalta_partner/biogalta_partner',
#             'objects': http.request.env['biogalta_partner.biogalta_partner'].search([]),
#         })

#     @http.route('/biogalta_partner/biogalta_partner/objects/<model("biogalta_partner.biogalta_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('biogalta_partner.object', {
#             'object': obj
#         })