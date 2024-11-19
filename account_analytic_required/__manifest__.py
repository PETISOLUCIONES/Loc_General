# Copyright Akretion - Alexis de Lattre
# Copyright Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Account Analytic Required",
    "version": "17.0.1.0.0",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account_usability","stock"],
    "data": ["views/account_account_views.xml",
             "views/stock_account_analytics.xml",
             ],
    "installable": True,
}
