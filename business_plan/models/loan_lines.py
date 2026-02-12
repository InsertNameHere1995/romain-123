from odoo import models, fields, api
import datetime


class forecastLoanLines(models.Model):
    _name = 'forecast.loan.lines'

    name = fields.Char(string="Name")
    loan_id = fields.Many2one(comodel_name='forecast.loan',inverse_name='loan_line_ids', string="Emprunt")
    monthly_payment_rel = fields.Float(related="loan_id.monthly_payment_amount", string="Mensualité")
    interest_portion = fields.Float(string="Q/P intérêts")
    capital_portion = fields.Float(string="Q/P Capital")
    outstanding_balance = fields.Float(string="SRD")
    new_outstanding_balance = fields.Float(compute='_compute_new_outstanding_balance', string="nouveau SRD")
    new_period_id = fields.Many2one(comodel_name="period",inverse_name="loan_lines_ids", string="Période")


    def _compute_new_outstanding_balance(self):
        for record in self:
            record.new_outstanding_balance = record.outstanding_balance - record.capital_portion
"""
period_id = self.env['period'].search([('business_project_id', '=', record.business_project_id.id),
                                                  ('period_id.start_date','<=',record.first_payment_date),
                                                  ('period_id.end_date','>=',record.first_payment_date)]).ensure_one()

                loan_lines = {}
                interest_portion = record.monthly_rate * outstanding_balance
                capital_portion = record.monthly_payment - interest_portion
                loan_lines['loan_id'] = record.id
                loan_lines['interest_portion'] = interest_portion
                loan_lines['capital_portion'] = capital_portion
                loan_lines['outstanding_balance'] = outstanding_balance

                record.loan_line_ids += record.create(loan_lines)

                outstanding_balance -= capital_portion


"""