# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
from dateutil.relativedelta import relativedelta
from . import roag_custom_function


class BusinessProject(models.Model):
    _name = 'business.project'
    _description = 'projet entrepreneurial'

    name = fields.Char(string="Name")
    founder_ids = fields.One2many("founder", 'business_project_id', string="Founders")
    entity_type = fields.Selection([('SRL', 'SRL'), ('SA', 'SA'), ('PP', 'Personne Physique'), ('SNC', 'SNC')],
                                   string="Type d'entreprise")
    legal_name = fields.Char(string="Raison Sociale - Nom de l'entreprise")
    public_name = fields.Char(string="Nom Public de l'entreprise (si différent de la Raison sociale)")
    address = fields.Char(string="Adresse du Siège Social")
    entity_zip = fields.Char(string="Code Postal")
    city = fields.Char(string="Ville")
    period_ids = fields.One2many("period", 'business_project_id', string="Périodes")
    forecast_income_ids = fields.One2many("forecast.income", 'business_project_id', string="Forecast Income")
    charges_ids = fields.One2many("charges", 'business_project_id', string="Charges")
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    share_capital = fields.Monetary(string="Apport/Capital de constitution")
    share_number = fields.Integer(string="Nombre d'actions/parts", default=1)
    share_value = fields.Monetary(compute="_compute_share_value", string="Valeur d'une action")
    forecast_loan_ids = fields.One2many('forecast.loan', 'business_project_id', string='Emprunts')
    first_fiscal_year_start = fields.Date(string="Date de début du premier exercice", default=datetime.date(2025,7,15))
    first_fiscal_year_end = fields.Date(string="Date de fin du premier exercice", default=datetime.date(2025, 12, 31))
    second_fiscal_year_start = fields.Date(compute='_compute_second_fiscal_year_start_date',
                                           string="Date de début du deuxième exercice")
    second_fiscal_year_end = fields.Date(compute='_compute_second_fiscal_year_end_date',
                                         string="Date de fin du deuxième exercice")
    third_fiscal_year_start = fields.Date(compute='_compute_third_fiscal_year_start_date',
                                          string="Date de début du troisième exercice")
    third_fiscal_year_end = fields.Date(compute='_compute_third_fiscal_year_end_date',
                                        string="Date de fin du troisième exercice")
    fourth_fiscal_year_start = fields.Date(compute='_compute_fourth_fiscal_year_start_date',
                                           string="Date de début du quatrième exercice")
    fourth_fiscal_year_end = fields.Date(compute='_compute_fourth_fiscal_year_end_date',
                                         string="Date de fin du quatrième exercice")
    coa_id = fields.Many2many('chart.of.account', 'coa_business_project_rel','coa_id','business_project_id', string= "Chart of Account")

    @api.depends('first_fiscal_year_end')
    def _compute_second_fiscal_year_start_date(self):
        for record in self:
            record.second_fiscal_year_start = record.first_fiscal_year_end + relativedelta(days=1)
            print('roag1 :', record.first_fiscal_year_start)

    @api.depends('first_fiscal_year_end')
    def _compute_second_fiscal_year_end_date(self):
        for record in self:
            record.second_fiscal_year_end = record.first_fiscal_year_end + relativedelta(years=1)

    @api.depends('second_fiscal_year_end')
    def _compute_third_fiscal_year_start_date(self):
        for record in self:
            record.third_fiscal_year_start = record.second_fiscal_year_end + relativedelta(days=1)

    @api.depends('second_fiscal_year_end')
    def _compute_third_fiscal_year_end_date(self):
        for record in self:
            record.third_fiscal_year_end = record.second_fiscal_year_end + relativedelta(years=1)

    @api.depends('third_fiscal_year_end')
    def _compute_fourth_fiscal_year_start_date(self):
        for record in self:
            record.fourth_fiscal_year_start = record.third_fiscal_year_end + relativedelta(days=1)

    @api.depends('third_fiscal_year_end')
    def _compute_fourth_fiscal_year_end_date(self):
        for record in self:
            record.fourth_fiscal_year_end = record.third_fiscal_year_end + relativedelta(years=1)



    @api.depends('share_number', 'share_capital')
    def _compute_share_value(self):
        for record in self:
            record.share_value = record.share_capital / record.share_number

    def _create_periods(self, data):
        # self.env['period'].create()
        return

    def get_period_count(self):
        period_count = 0
        delta = relativedelta(self.first_fiscal_year_end, self.first_fiscal_year_start)

        if delta.years > 0:
            period_count += (delta.years * 12)

        if delta.months > 0:
            period_count += delta.months

        period_count += 36  # adding 36 months because we work w/ 4 fiscal years (First fiscal year + 3 years)

        return period_count


    def get_all_periods_to_create(self):
        all_periods_list = []
        start_date = self.first_fiscal_year_start
        print()
        print("roag :", start_date, self.first_fiscal_year_start)
        print()
        end_date = roag_custom_function.get_last_day_of_month(self.first_fiscal_year_start)
        period_count = self.get_period_count()

        for i in range(0, period_count + 1):
            period_data = {}

            period_data['start_date'] = start_date
            period_data['end_date'] = end_date

            all_periods_list.append(period_data)
            print(all_periods_list)

            new_end_date = roag_custom_function.get_last_day_of_next_month(start_date)
            new_start_date = roag_custom_function.get_first_day_of_next_month(start_date)
            start_date = new_start_date
            end_date = new_end_date

        return all_periods_list


    @api.model_create_multi
    def create(self, vals):
        business_plans = super(BusinessProject, self).create(vals)
        for business_plan in business_plans:
            print('roag 3 :', business_plan.first_fiscal_year_start)
            all_periods_list = business_plan.get_all_periods_to_create()


            for period in all_periods_list:
                period_info = {
                        'business_project_id': business_plan.id,
                        'start_date': period['start_date'],
                        'end_date': period['end_date'],
                    }
                self.env['period'].create(period_info)
        return business_plans
