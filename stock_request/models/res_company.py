
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_request_allow_virtual_loc = fields.Boolean(
        string="Allow Virtual locations on Stock Requests"
    )
    stock_request_check_available_first = fields.Boolean(
        string="Check available stock first"
    )
