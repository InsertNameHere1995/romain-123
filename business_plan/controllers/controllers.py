# -*- coding: utf-8 -*-
# from odoo import http


# class PlanFinancier(http.Controller):
#     @http.route('/plan_financier/plan_financier', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plan_financier/plan_financier/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('plan_financier.listing', {
#             'root': '/plan_financier/plan_financier',
#             'objects': http.request.env['plan_financier.plan_financier'].search([]),
#         })

#     @http.route('/plan_financier/plan_financier/objects/<model("plan_financier.plan_financier"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plan_financier.object', {
#             'object': obj
#         })

