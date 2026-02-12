# -*- coding: utf-8 -*-
{
    'name': "financial_plan",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'application': True,

    'description': "description",

    'author': "Romain",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/business_project.xml',
        'views/forecast_income.xml',
        'views/founder.xml',
        'views/period.xml',
        'views/payment_terms.xml',
        'views/loan.xml',
        'views/chart_of_account.xml',
        'data/settings.xml',
        'data/chart_of_account.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

