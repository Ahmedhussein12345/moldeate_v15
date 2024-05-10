# -*- coding: utf-8 -*-
# from odoo import http


# class GlobalSearch(http.Controller):
#     @http.route('/global_search/global_search', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/global_search/global_search/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('global_search.listing', {
#             'root': '/global_search/global_search',
#             'objects': http.request.env['global_search.global_search'].search([]),
#         })

#     @http.route('/global_search/global_search/objects/<model("global_search.global_search"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('global_search.object', {
#             'object': obj
#         })
