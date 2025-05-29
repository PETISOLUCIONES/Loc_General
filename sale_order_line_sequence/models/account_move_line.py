# Copyright 2023 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    related_so_sequence = fields.Char(
        string="#",
        help="Número de línea.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._set_related_so_sequence()
        return lines

    def _set_related_so_sequence(self):
        secuencia = 1
        for line in self:
            line.related_so_sequence = secuencia
            secuencia += 1

    def get_invoice_line_dict(self, index):
        line_dict = super(AccountMoveLine, self).get_invoice_line_dict(index)
        if line_dict and self.related_so_sequence:
            line_dict['NumItem'] = self.related_so_sequence
        return line_dict

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_dict_lineas_fact(self):
        self.invoice_line_ids._set_related_so_sequence()
        data = super(AccountMove, self).get_dict_lineas_fact()
        return data
