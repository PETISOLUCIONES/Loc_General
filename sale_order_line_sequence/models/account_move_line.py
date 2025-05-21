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

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_dict_lineas_fact(self):
        datos = super(AccountMove, self).get_dict_lineas_fact()
        self.invoice_line_ids._set_related_so_sequence()
        for i, line in enumerate(self.invoice_line_ids.sorted(key=lambda l: l.price_subtotal, reverse=True),  start=0):
            if line.display_type != 'line_section' and line.display_type != 'line_note':
                try:
                    datos['datos'][i]['NumItem'] = line.related_so_sequence if line.related_so_sequence else 0
                except:
                    pass
        return datos
