# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime

invoicing_recurrence_matching = {'weekly':0.25,'biweekly':0.5,'monthly':1,'quarterly':3,'half-yearly':6,'yearly':12}

class forecast_income(models.Model):
    _name='forecast.income'
    _description='forecast_incomes'

    name = fields.Char(string="Nom du Revenu")
    type = fields.Selection([('SH',"Service (Tarif horaire et nombre d'heures)"),('product',"Produit (Prix unitaire et quantités)"),('subscription','Abonnement'),('other',"Autre (montant)")])
    start_date = fields.Date(string="Date de début du revenu", default=datetime.date.today())
    unit_price = fields.Float(string="Prix Unitaire")
    discount = fields.Float(string="Remise en %")
    qty = fields.Float(string="Quantité")
    is_recurring = fields.Boolean(string="Est récurrent ?", default=False)
    invoicing_recurrence = fields.Selection([('weekly', "Weekly"),('biweekly','Bi weekly (every 2 weeks)'),('monthly', 'Monthly'),('quarterly','Quarterly'),('half-yearly','Semestriel'),('yearly','Annuel')],default='monthly')
    end_date = fields.Date(string="Date de résiliation du revenu")
    #vat_id = fields.Many2one(comodel_name= 'account.tax.amount', string='TVA')
    amount_no_vat = fields.Float(compute='_compute_amount',string="Montant Total HTVA")
    vat_amount = fields.Float(compute='_compute_vat_amount', string= 'Montant de la TVA')
    amount_with_vat = fields.Float(compute='_compute_amount_with_vat', string="Montant TTC")
    business_project_id = fields.Many2one(comodel_name='business.project', inverse_name='forecast_income_ids',string="Business Project")
    revenue_period_ids = fields.Many2many('period','forecast_income_period_rel', 'forecast_income_id', 'period_id',string="Liste des revenus facturés")
    cashflow_period_ids = fields.Many2many('period', 'forecast_cashflow_income_period_rel', 'forecast_cashflow_income_id', 'period_id', string="Liste des revenus perçus.")
    payment_terms_id = fields.Many2one(comodel_name='payment.terms', inverse_name='forecast_income_ids', string="Payment terms")
    account_id = fields.Many2one(comodel_name='chart.of.account', inverse_name='income_ids', string='Compte de Revenus')

    def _compute_amount(self):
        for record in self:
            record.amount_no_vat = record.qty * record.unit_price *(1-record.discount)
            record.amount_no_vat = record.qty * record.unit_price *(1-record.discount)

    def _compute_vat_amount(self):
        vat = 0.21
        for record in self:
            record.vat_amount = (record.amount_no_vat * (1+vat)) - record.amount_no_vat
            #* record.vat_id.amount

    def _compute_amount_with_vat(self):
        for record in self:
            record.amount_with_vat = record.amount_no_vat + record.vat_amount
        






