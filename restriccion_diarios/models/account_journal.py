# -*- coding: utf-8 -*-
"""
Módulo: Restricción de Diarios por Usuario
Archivo: models/account_journal.py

Este archivo extiende el modelo account.journal para implementar restricciones
de acceso basadas en usuarios.
"""

from odoo import api, fields, models
from odoo.osv import expression


class ShAccountJournalRestrict(models.Model):
    """
    Extiende account.journal para agregar restricciones de usuarios.

    Funcionalidad principal:
    - Permite asignar usuarios específicos a cada diario
    - Filtra automáticamente los diarios según el usuario actual
    - Aplica valores por defecto desde configuración de compañía
    """
    _inherit = 'account.journal'

    @api.model
    def default_get(self, fields):
        """
        Establece valores por defecto al crear un nuevo diario.

        Funcionamiento:
        - Obtiene los usuarios por defecto desde la configuración de la compañía
        - Los asigna automáticamente al campo user_ids del nuevo diario

        Configuración:
        - Los usuarios por defecto se configuran en:
          Configuración > Contabilidad > "Diarios y Usuarios por Defecto"
        - Se almacenan en: self.env.company.sh_user_ids

        Args:
            fields (list): Lista de campos para los que se solicitan valores por defecto

        Returns:
            dict: Diccionario con valores por defecto, incluyendo user_ids

        Ejemplo:
            Si sh_user_ids = [Usuario A, Usuario B]
            Entonces el nuevo diario tendrá user_ids = [Usuario A, Usuario B]
        """
        rec = super(ShAccountJournalRestrict, self).default_get(fields)

        # Obtiene IDs de usuarios por defecto desde configuración de compañía
        users = self.env.company.sh_user_ids.ids

        # Actualiza el diccionario de valores por defecto
        # (6, 0, users) = Reemplaza todos los registros con la lista users
        rec.update({
            'user_ids': [(6, 0, users)]
        })
        return rec

    user_ids = fields.Many2many(
        'res.users',
        string="Usuarios",
        copy=False,
        help="Usuarios que tienen permiso para acceder a este diario. "
             "Si el usuario tiene el grupo 'Habilitar Restricción de Diarios', "
             "solo podrá ver/usar los diarios donde esté incluido en este campo.")

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """
        Sobrescribe la búsqueda de diarios para aplicar restricciones.

        Este método se ejecuta cuando:
        - Se busca un diario en campos de selección (ej: al crear una factura)
        - Se escribe en un campo many2one o many2many de diarios
        - Se usa autocompletado en cualquier vista

        Lógica de restricción:
        - Si el usuario tiene "group_journal_restrict_feature" Y NO es administrador:
            * Filtra para mostrar solo diarios donde user_ids contenga al usuario actual
        - Si el usuario es administrador O NO tiene el grupo:
            * Muestra todos los diarios (sin filtro adicional)

        Args:
            name (str): Texto de búsqueda ingresado por el usuario
            domain (list): Dominio de búsqueda adicional
            operator (str): Operador de comparación (por defecto 'ilike')
            limit (int): Número máximo de resultados
            order (str): Orden de los resultados

        Returns:
            list: Lista de IDs de diarios que coinciden con la búsqueda

        Ejemplo:
            Usuario con restricciones busca "Banco":
            - Solo verá diarios con "Banco" en el nombre Y donde esté asignado

            Administrador busca "Banco":
            - Verá todos los diarios con "Banco" en el nombre
        """
        # Verifica si aplicar restricciones
        if (
            self.env.user.has_group("restriccion_diarios.group_journal_restrict_feature") and not
            (self.env.user.has_group("restriccion_diarios.group_access_of_assign_user"))
        ):
            # Usuario tiene restricciones: filtrar por user_ids
            sh_domain = [
                ("user_ids", "in", self.env.user.id),  # Solo diarios asignados
                ('name', 'ilike', name)                # Que coincidan con el nombre buscado
            ]
        else:
            # Usuario sin restricciones: solo filtrar por nombre
            sh_domain = [('name', 'ilike', name)]

        # Combina el dominio de restricción con el dominio original usando AND
        return super()._name_search(name, expression.AND([sh_domain, domain]), operator, limit, order)

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        """
        Sobrescribe la búsqueda/listado de diarios para aplicar restricciones.

        Este método se ejecuta cuando:
        - Se abre la vista de lista de diarios (Contabilidad > Configuración > Diarios)
        - Se cargan diarios en reportes
        - Se ejecuta cualquier búsqueda programática de diarios
        - Se accede al menú de diarios desde el dashboard

        Lógica de restricción:
        - Si el usuario tiene "group_journal_restrict_feature" Y NO es administrador:
            * Agrega filtro para mostrar solo diarios donde user_ids contenga al usuario actual
        - Si el usuario es administrador O NO tiene el grupo:
            * No agrega filtro (muestra todos los diarios según domain original)

        Diferencia con _name_search:
        - _name_search: Para búsquedas/autocompletado en campos
        - search_fetch: Para vistas de lista, menús, y búsquedas generales

        Args:
            domain (list): Dominio de búsqueda (condiciones de filtrado)
            field_names (list): Campos a recuperar de la base de datos
            offset (int): Número de registros a saltar (para paginación)
            limit (int): Número máximo de registros a retornar
            order (str): Orden de los resultados

        Returns:
            RecordSet: Conjunto de registros de diarios que cumplen las condiciones

        Nota técnica:
        - Modifica el domain IN-PLACE usando +=
        - El filtro se agrega como una condición AND adicional

        Ejemplo de uso:
            Usuario restringido abre "Contabilidad > Diarios":
            - Solo ve diarios asignados a él en user_ids

            Administrador abre "Contabilidad > Diarios":
            - Ve todos los diarios de la compañía
        """
        _ = self._context or {}  # Obtiene contexto (no usado actualmente)

        # Verifica si aplicar restricciones
        if (
            self.env.user.has_group("restriccion_diarios.group_journal_restrict_feature") and not
            (self.env.user.has_group("restriccion_diarios.group_access_of_assign_user"))
        ):
            # Usuario tiene restricciones: agregar filtro al domain
            domain += [
                ("user_ids", "in", self.env.user.id),  # Solo diarios donde esté asignado
            ]

        # Llama al método padre con el domain modificado
        return super(ShAccountJournalRestrict, self).search_fetch(
            domain, field_names, offset, limit, order)
