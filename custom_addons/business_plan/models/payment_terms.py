from odoo import models, fields, api
import datetime


class payment_terms(models.Model):
    _name = "payment.terms"

    name = fields.Char(string="Nom")
    is_end_of_month = fields.Boolean(string= "Fin de mois ?", default=False)
    days = fields.Integer(string="Nbre de jours", default=1)
    forecast_income_ids = fields.One2many('forecast.income','payment_terms_id', string='Revenus')
    charges_ids = fields.One2many('charges', 'payment_terms_id', string='Charges')


"""    def _compute_default_days(self):
        self.days = 1

"""