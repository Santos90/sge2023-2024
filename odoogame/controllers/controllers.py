# -*- coding: utf-8 -*-
# from odoo import http


# class Odoogame(http.Controller):
#     @http.route('/odoogame/odoogame', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoogame/odoogame/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoogame.listing', {
#             'root': '/odoogame/odoogame',
#             'objects': http.request.env['odoogame.odoogame'].search([]),
#         })

#     @http.route('/odoogame/odoogame/objects/<model("odoogame.odoogame"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoogame.object', {
#             'object': obj
#         })
