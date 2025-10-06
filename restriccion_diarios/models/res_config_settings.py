# -*- coding: utf-8 -*-
"""
Módulo: Restricción de Diarios por Usuario
Archivo: models/res_config_settings.py

Este archivo extiende los modelos de configuración para permitir establecer
valores por defecto a nivel de compañía para diarios y usuarios.
"""

from odoo import fields, models


class ResCompany(models.Model):
    """
    Extiende res.company para almacenar configuraciones por defecto.

    Propósito:
    - Almacenar a nivel de compañía los valores por defecto para:
        * Diarios que se asignarán a nuevos usuarios
        * Usuarios que se asignarán a nuevos diarios

    Almacenamiento:
    - Los valores se guardan en la tabla res_company
    - Cada compañía puede tener sus propios valores por defecto
    - Persisten en la base de datos de forma permanente

    Uso:
    - Estos campos son utilizados por los métodos default_get de:
        * account_journal.py: Usa sh_user_ids para nuevos diarios
        * res_users.py: Usa journal_ids para nuevos usuarios
    """
    _inherit = 'res.company'

    journal_ids = fields.Many2many(
        'account.journal',
        string="Diarios",
        help="Diarios que se asignarán automáticamente a los nuevos usuarios. "
             "Cuando se crea un usuario, estos diarios se añadirán a su campo journal_ids.")

    sh_user_ids = fields.Many2many(
        'res.users',
        string="Usuarios",
        help="Usuarios que se asignarán automáticamente a los nuevos diarios. "
             "Cuando se crea un diario, estos usuarios se añadirán a su campo user_ids.")


class ResConfigSettings(models.TransientModel):
    """
    Extiende res.config.settings para exponer campos de configuración en UI.

    Propósito:
    - Permitir la edición de los valores por defecto desde la interfaz
    - Actúa como puente entre la UI y el modelo res.company

    Modelo Transient:
    - Este modelo NO almacena datos directamente
    - Los datos se guardan en res.company a través de los campos relacionados

    Acceso:
    - Disponible en: Configuración > Contabilidad
    - Sección: "Diarios y Usuarios por Defecto"
    - Vista definida en: views/res_config_settings_views.xml

    Campos relacionados:
    - related='company_id.journal_ids': Lee/escribe en la compañía actual
    - readonly=False: Permite edición (por defecto related fields son readonly)
    """
    _inherit = 'res.config.settings'

    journal_ids = fields.Many2many(
        related='company_id.journal_ids',
        readonly=False,
        help="Diarios por defecto para nuevos usuarios de esta compañía.")

    sh_user_ids = fields.Many2many(
        related='company_id.sh_user_ids',
        readonly=False,
        help="Usuarios por defecto para nuevos diarios de esta compañía.")
