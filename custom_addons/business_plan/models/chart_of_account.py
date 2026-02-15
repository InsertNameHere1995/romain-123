from odoo import models, fields, api



class ChartOfAccount(models.Model):
    _name='chart.of.account'

    name = fields.Char(string="Nom du compte")
    code = fields.Char(string="Code", size=6)
    business_project_id = fields.Many2many('business.project', 'coa_business_project_rel','business_project_id','coa_id', string='Projet Entrepreneurial')
    charge_ids = fields.Many2one(comodel_name='charges', inverse_name='account_id', string='Charge')
    income_ids = fields.Many2one(comodel_name='forecast.income', inverse_name='account_id', string='Revenus')
