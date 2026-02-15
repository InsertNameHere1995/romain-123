from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime
from . import forecast_income
from . import roag_custom_function


class period(models.Model):
    _name='period'
    _description='period'

    start_date = fields.Date(string="Date de début",default=datetime.date.today())
    end_date = fields.Date(string="Date de fin",default=datetime.date.today())
    business_project_id = fields.Many2one(comodel_name="business.project",inverse_name='period_ids', string="Projet/Legal Entity")
    fiscal_year_number = fields.Integer(compute="_compute_fiscal_year_number")
    is_fiscal_year_end = fields.Boolean(compute="_compute_is_fiscal_year_end()",string="Mois de fin de période fiscale ?")
    name = fields.Char(compute="_compute_period_name", string="Nom de la période")
    invoiced_income_ids = fields.Many2many('forecast.income', 'forecast_income_period_rel', 'forecast_income_id',
                                           'period_id', compute='_compute_invoiced_income_ids', string="Liste des revenus facturés")

    invoiced_income_amount_no_vat = fields.Float(compute='_compute_invoiced_income_amount_no_vat',string="Montant facturé sur période", store=True)
    cashflow_income_ids = fields.Many2many('forecast.income', 'forecast_cashflow_income_period_rel', 'forecast_cashflow_income_id',
                                          'period_id', compute='_compute_cashflow_income_ids', string="Liste des revenus perçus")
    cashflow_income_amount_with_vat = fields.Float(compute='_compute_cashflow_income_amount_with_vat', string='Montant encaissé', store=True)
    invoiced_charges_ids = fields.Many2many('charges', 'charges_period_rel', 'charges_id',
                                          'period_id', compute='_compute_charges_ids', string="Liste des charges facturées")

    loan_lines_ids = fields.One2many('forecast.loan.lines','new_period_id', string="Ligne de prêt")

    def get_payment_date(self, model, date):
        payment_terms_id = model.payment_terms_id
        if payment_terms_id.is_end_of_month:
            date = roag_custom_function.get_last_day_of_month(date)

        date += datetime.timedelta(days=payment_terms_id.days)
        return date

    def _compute_charges_ids(self):
        for period in self:
            period.invoiced_charges_ids = []
            list = []
            charges_list = self.env['charges'].search([('business_project_id', '=', period.business_project_id.id)])
            for charge in charges_list:
                to_be_recorded = True
                if charge.start_date >= period.start_date and charge.start_date <= period.end_date:
                    list.append(charge.id)
                if charge.is_recurring == True:
                    if charge.end_date:
                        if period.end_date >= charge.end_date:
                            to_be_recorded = False
                    if period.end_date <= charge.start_date:
                        to_be_recorded = False
                    if to_be_recorded == True:
                        delta = relativedelta(charge.start_date, period.end_date)
                        month_delta = (delta.years * 12) + delta.months
                        coef = forecast_income.invoicing_recurrence_matching[charge.recurrence]
                        print("New delta :", delta)
                        is_counted_period = False
                        if coef > 0 and coef < 1:
                            is_counted_period = True
                        if coef >= 1:
                            if month_delta % coef == 0:
                                is_counted_period = True
                        if is_counted_period:
                            list.append(charge.id)
            period.write({'invoiced_charges_ids': list})

    def _compute_cashflow_income_amount_with_vat(self):
        for record in self:
            amount = 0
            for revenue in record.cashflow_income_ids:
                amount += revenue.amount_with_vat

            record.cashflow_income_amount_with_vat = amount



    def _compute_cashflow_income_ids(self):
        for period in self:
            period.invoiced_income_ids = []
            list = []
            income_list = self.env['forecast.income'].search([('business_project_id', '=', period.business_project_id.id)])
            for revenue in income_list:
                new_start_date = self.get_payment_date(revenue,revenue.start_date)
                if new_start_date >= period.start_date and new_start_date <= period.end_date:
                    list.append(revenue.id)

                if revenue.is_recurring:
                    to_be_cashed_in = True
                    if revenue.end_date:
                        if period.end_date >= self.get_payment_date(revenue, revenue.end_date):
                            to_be_cashed_in = False
                    if period.end_date <= new_start_date:
                        to_be_cashed_in = False
                    if to_be_cashed_in == True:
                        delta = relativedelta(new_start_date, period.end_date)
                        month_delta = (delta.years * 12) + delta.months
                        coef = forecast_income.invoicing_recurrence_matching[revenue.invoicing_recurrence]
                        is_cash_period = False
                        if coef > 0 and coef < 1:
                            is_cash_period = True
                        if coef >= 1:
                            if month_delta % coef == 0:
                                is_cash_period = True
                        if is_cash_period:
                            list.append(revenue.id)
                            print('list',list)

            period.write({'cashflow_income_ids': list})

    def _compute_invoiced_income_amount_no_vat(self):
        for record in self:
            amount = 0
            for revenue in record.invoiced_income_ids:
                amount += revenue.amount_no_vat

            record.invoiced_income_amount_no_vat = amount

    def _compute_invoiced_income_ids(self):
        for period in self:
            period.invoiced_income_ids = []
            list = []
            print('P :',period.business_project_id.id)
            income_list = self.env['forecast.income'].search([('business_project_id', '=', period.business_project_id.id)])
            for revenue in income_list:
                print('revenue :',revenue.start_date)
                if revenue.start_date >= period.start_date and revenue.start_date <= period.end_date:
                    print('roag error', period.invoiced_income_ids)
                    list.append(revenue.id)


                if revenue.is_recurring:
                    to_be_invoiced = True
                    if revenue.end_date:
                        if period.end_date >= revenue.end_date:
                            to_be_invoiced = False
                    if period.end_date <= revenue.start_date:
                        to_be_invoiced = False
                        print('roag exit')
                    if to_be_invoiced == True:
                        delta = relativedelta(revenue.start_date, period.end_date)
                        month_delta = (delta.years * 12) + delta.months
                        coef = forecast_income.invoicing_recurrence_matching[revenue.invoicing_recurrence]
                        is_invoiced_period = False
                        if coef > 0 and coef < 1:
                            is_invoiced_period = True
                        if coef >= 1:
                            if month_delta % coef == 0:
                                is_invoiced_period = True
                        if is_invoiced_period:
                            list.append(revenue.id)

            period.write({'invoiced_income_ids': list})


                #record.invoiced_income_ids = income_list




    @api.depends('end_date')
    def _compute_period_name(self):
        for record in self:
            record.name = f'{record.end_date.strftime("%B")} {record.end_date.strftime("%Y")}'


    @api.depends('end_date','business_project_id.first_fiscal_year_end',
                 'business_project_id.second_fiscal_year_end',
                 'business_project_id.third_fiscal_year_end',
                 'business_project_id.fourth_fiscal_year_end',
                 )
    def _compute_fiscal_year_number(self):
        for record in self:
            if record.start_date >= record.business_project_id.first_fiscal_year_start and record.end_date <= record.business_project_id.first_fiscal_year_end:
                self.fiscal_year_number = 1
            elif record.start_date >= record.business_project_id.second_fiscal_year_start and record.end_date <= record.business_project_id.second_fiscal_year_end:
                self.fiscal_year_number = 2
            elif record.start_date >= record.business_project_id.third_fiscal_year_start and record.end_date <= record.business_project_id.third_fiscal_year_end:
                self.fiscal_year_number = 3
            elif record.start_date >= record.business_project_id.fourth_fiscal_year_start and record.end_date <= record.business_project_id.fourth_fiscal_year_end:
                self.fiscal_year_number = 4
    @api.depends('end_date','business_project_id.first_fiscal_year_end',
                 'business_project_id.second_fiscal_year_end',
                 'business_project_id.third_fiscal_year_end',
                 'business_project_id.fourth_fiscal_year_end',
                 )
    def _compute_is_fiscal_year_end(self):
        for record in self:
            if record.end_date == record.business_project_id.first_fiscal_year_end:
                record.is_fiscal_year_end = True
            elif record.end_date == record.business_project_id.second_fiscal_year_end:
                record.is_fiscal_year_end = True
            elif record.end_date == record.business_project_id.third_fiscal_year_end:
                record.is_fiscal_year_end = True
            elif record.end_date == record.business_project_id.fourth_fiscal_year_end:
                record.is_fiscal_year_end = True

            else :
                record.is_fiscal_year_end = False





