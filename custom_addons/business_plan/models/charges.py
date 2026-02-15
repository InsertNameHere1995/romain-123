from odoo import models, fields, api
import datetime

class Charges(models.Model):
    _name = 'charges'


    name = fields.Char(string="Nom de la charge")
    business_project_id = fields.Many2one(comodel_name='business.project', inverse_name='csharges_ids',
                                          string="Business Project")
    qty = fields.Float(string="Quantité")
    amount = fields.Float(string="Montant")
    is_recurring = fields.Boolean(default=False, string= "Charge récurrente ?")
    recurrence = fields.Selection([('monthly', 'Mensuel'), ('quarterly', 'Trimestriel'),('semestrial', 'Semestriel'),('yearly', 'Annuel')], string='Périodicité', default="monthly")
    start_date = fields.Date(string="Date de début", default=datetime.date.today())
    end_date = fields.Date(string="Date de fin")
    #vat_id = fields.Many2one(comodel_name='account.tax.amount', string='TVA')
    amount_no_vat = fields.Float(compute='_compute_total_amount_no_vat',string="Montant total HTVA")
    amount_with_vat = fields.Float(compute='_compute_total_amount_with_vat',string="Montant total TTC")
    vat_amount = fields.Float(compute='_compute_vat_amount',string="Montant TVA")
    invoiced_period_ids = fields.Many2many('period', 'charges_period_rel',
                                           'charges_id', 'period_id', string="Liste des charges facturées.")
    payment_terms_id = fields.Many2one(comodel_name='payment.terms', inverse_name='charges_ids',
                                       string="Payment terms")
    account_id = fields.Many2one(comodel_name='chart.of.account',inverse_name='charge_ids', string='Compte de charge', default="financial_plan.610000")



    def _compute_total_amount_no_vat(self):
        for charge in self:
            charge.amount_no_vat = charge.qty * charge.amount

    def _compute_vat_amount(self):
        vat = 0.21
        for charge in self:
            charge.vat_amount = (charge.amount_no_vat * (1+vat)) - charge.amount_no_vat

    def _compute_total_amount_with_vat(self):
        for charge in self:
            charge.amount_with_vat = charge.amount_no_vat + charge.vat_amount
