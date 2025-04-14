# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Jumana Haseen (<https://www.cybrosys.com>)

#    you can modify it under the terms of the GNU AFFERO GENERAL
#    PUBLIC LICENSE (AGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC
#    LICENSE (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from validate_email import validate_email
from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    """Inherited module to execute a function when work_email
    record is saved"""
    _inherit = 'hr.employee'

    @api.onchange('work_email')
    def _check_work_email(self):
        """
        Check the work email is valid or not
        """
        if self.work_email:
            is_valid = validate_email(self.work_email, check_mx=False,
                                      verify=True, debug=False,
                                      smtp_timeout=10)
            if not is_valid:
                warning = {
                    'title': _('Advertencia de validación de correo electrónico'),
                    'message': _('La dirección de correo electrónico "%s" parece no ser válida o no existe. '
                                 ) % self.work_email
                }
                return {'warning': warning}
