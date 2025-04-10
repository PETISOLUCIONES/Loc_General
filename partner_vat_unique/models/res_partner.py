# Copyright 2017 Grant Thornton Spain - Ismael Calvo <ismael.calvo@es.gt.com>
# Copyright 2020 Manuel Calero - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat = fields.Char(copy=False)

    @api.constrains("vat", "parent_id")
    def _check_vat_unique(self):
        for record in self:
            # Si tiene un padre o no tiene identificación
            if bool(record.parent_id) or not bool(record.vat):
                continue
            # Si se está importando maestras
            from_import = self.env.context.get("import_file")
            if bool(from_import):
                continue
            # Si se está en etapa de pruebas
            test_condition = config["test_enable"] and not self.env.context.get("test_vat")
            if bool(test_condition):
                continue
            # Si hay contactos con la misma identificación (_compute_same_vat_partner_id)
            if bool(record.same_vat_partner_id):
                raise ValidationError(_("The VAT %s already exists in another partner.") % record.vat)
