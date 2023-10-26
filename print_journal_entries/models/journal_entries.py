# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import models, fields
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    dr_total = fields.Monetary(string="Debe", default=0.0, compute="total_debit_credit")
    cr_total = fields.Monetary(string="Haber", default=0.0, compute="total_debit_credit")

    def total_debit_credit(self):
        for move in self:
            dr_total = 0.0
            cr_total = 0.0
            for line in move.line_ids:
                dr_total += line.debit
                cr_total += line.credit
            move.dr_total, move.cr_total = dr_total, cr_total
