# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Stock Picking Return Invoicing",
    "summary": "Add an option to refund returned pickings",
    "version": "17.0.1.0.0",
    "category": "Purchases",
    'author': "PETI Soluciones Productivas",
    'website': "http://www.peti.com.co",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["purchase_stock","purchase_force_invoiced"],
    "data": ["views/account_invoice_view.xml", "views/purchase_view.xml"],
}
