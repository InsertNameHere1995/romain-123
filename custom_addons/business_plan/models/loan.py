from odoo import models, fields, api
import datetime


class forecastLoan(models.Model):
    _name = 'forecast.loan'

    name = fields.Char(string='Name')
    business_project_id = fields.Many2one(comodel_name='business.project', inverse_name='forecast_loan_ids',
                                          string="Business Project")
    yearly_rate = fields.Float(string='Taux annuel')
    loan_amount = fields.Float(string='Loan Amount')
    payment_count = fields.Integer(string='Mensuality count')
    monthly_rate = fields.Float(compute='_compute_monthly_rate', string='Taux mensuel')
    monthly_payment_amount = fields.Float(compute= '_compute_monthly_payment_amount' ,string='Mensualité')
    first_payment_date = fields.Date(default=datetime.date.today(), string='Date de la première mensualité')
    v12 = fields.Float(compute='_compute_v12', string="v12")
    loan_line_ids = fields.One2many(comodel_name='forecast.loan.lines', inverse_name='loan_id', compute="_compute_loan_lines_ids", string="Lignes de prêt")


    def _compute_monthly_rate(self):
        for record in self:
            record.monthly_rate = ((1+record.yearly_rate)**(1/12))-1
    def _compute_v12(self):
        for record in self:
            i12= record.monthly_rate
            record.v12 = 1/(1+i12)
    def _compute_loan_lines_ids(self):
        for record in self:
            outstanding_balance = record.loan_amount
            loan_lines_list = []
            for line in range(record.payment_count):
                loan_lines = {}
                interest_portion = record.monthly_rate * outstanding_balance
                capital_portion = record.monthly_payment_amount - interest_portion
                loan_lines['loan_id'] = record.id
                loan_lines['interest_portion'] = interest_portion
                loan_lines['capital_portion'] = capital_portion
                loan_lines['outstanding_balance'] = outstanding_balance

                loan_lines_list.append(loan_lines)

                outstanding_balance -= capital_portion

            list = self.env['forecast.loan.lines'].create(loan_lines_list)
            record.loan_line_ids = list

    def _compute_monthly_payment_amount(self):
        for record in self:
            i12 = record.monthly_rate
            v12 = record.v12
            record.monthly_payment_amount = (record.loan_amount*i12)/(1-(v12**record.payment_count))
