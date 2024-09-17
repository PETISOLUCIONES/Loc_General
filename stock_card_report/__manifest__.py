# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Card Report",
    "summary": "Add stock card report on Inventory Reporting.",
    "version": "17.0.1.0.1",
    "category": "Warehouse",
    "website": "https://github.com/OCA/stock-logistics-reporting",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "date_range", "report_xlsx_helper"],
    "data": [
        "data/report_data.xml",
        "security/ir.model.access.csv",
        "reports/stock_card_report.xml",
        "data/paper_format.xml",
        "wizard/stock_card_report_wizard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_card_report/static/src/css/**/*",
            "stock_card_report/static/src/js/stock_card_report_backend.esm.js",
            "stock_card_report/static/src/js/owl_template.xml"
        ]
    },
    "installable": True,
}
