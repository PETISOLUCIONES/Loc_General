# -*- coding: utf-8 -*-

{
    'name': "Diarios habilitados por usuario",
    'summary': "Diarios habilitados por usuario",
    'description': """
        Este módulo permite habilitar diarios por cada usuario.
    """,
    'author': "PETI Soluciones Productivas",
    'website': "http://peti.erp.com.co",
    'category': 'Accounting',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'sale',
        'account',
        'account_asset',
        'account_reports',
        'reports_accounting',
        'account_debit_note',
        'account_loan',
        'account_online_synchronization',
        'account_auto_transfer',
        'account_commission',
        'bi_cs_multiple_payment',
        'documents_account',
        'documents',
        'hr_expense_extract',
        'account_financial_report',
        'th360_hr_social_security',
        'hr_expense',
        'hr_expense_extract',
        'th360_hr_loan',
        'hr_payroll_anticipos',
        'th360_hr_payroll',
        'hr_payroll',
        'import_fac_electronica',
        'payment',
        'point_of_sale',
        'product',
        'sale_management',
        'stock_landed_costs',
        'stock_account',
        'stock',
        'trial_balance_pdf',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
    ],
    'sequence': 1,
    'application': True,
    'installable': True,
    'auto_install': False,
}