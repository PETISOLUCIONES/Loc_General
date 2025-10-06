# -*- coding: utf-8 -*-
"""
Módulo: Restricción de Diarios por Usuario
Archivo: models/res_users.py

Este archivo extiende el modelo res.users para permitir la asignación
de diarios específicos a cada usuario.
"""

from odoo import api, fields, models


class ShResUsers(models.Model):
    """
    Extiende res.users para agregar la relación con diarios permitidos.

    Funcionalidad principal:
    - Permite asignar diarios específicos a cada usuario
    - Aplica valores por defecto desde configuración de compañía
    - Complementa la restricción definida en account.journal

    Relación bidireccional:
    - res.users.journal_ids -> account.journal (diarios del usuario)
    - account.journal.user_ids -> res.users (usuarios del diario)
    """
    _inherit = 'res.users'

    @api.model
    def default_get(self, fields):
        """
        Establece valores por defecto al crear un nuevo usuario.

        Funcionamiento:
        - Obtiene los diarios por defecto desde la configuración de la compañía
        - Los asigna automáticamente al campo journal_ids del nuevo usuario

        Configuración:
        - Los diarios por defecto se configuran en:
          Configuración > Contabilidad > "Diarios y Usuarios por Defecto"
        - Se almacenan en: self.env.company.journal_ids

        Args:
            fields (list): Lista de campos para los que se solicitan valores por defecto

        Returns:
            dict: Diccionario con valores por defecto, incluyendo journal_ids

        Ejemplo:
            Si journal_ids (de compañía) = [Diario Ventas, Diario Compras]
            Entonces el nuevo usuario tendrá journal_ids = [Diario Ventas, Diario Compras]

        Nota:
            - Este método solo afecta la creación de NUEVOS usuarios
            - Los usuarios existentes NO se modifican
            - Es complementario al default_get de account_journal.py
        """
        rec = super(ShResUsers, self).default_get(fields)

        # Obtiene IDs de diarios por defecto desde configuración de compañía
        journals = self.env.company.journal_ids.ids

        # Actualiza el diccionario de valores por defecto
        # (6, 0, journals) = Reemplaza todos los registros con la lista journals
        rec.update({
            'journal_ids': [(6, 0, journals)]
        })
        return rec

    journal_ids = fields.Many2many(
        'account.journal',
        string="Diarios",
        copy=False,
        help="Diarios a los que este usuario tiene acceso. "
             "Si el usuario tiene el grupo 'Habilitar Restricción de Diarios', "
             "solo podrá ver/usar estos diarios en el sistema.")
