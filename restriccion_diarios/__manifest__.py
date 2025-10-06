# -*- coding: utf-8 -*-
{
    "name": "Restricción de Diarios por Usuario",
    "author": "PETI Soluciones Productivas",
    "license": "LGPL-3",
    "website": "",
    "support": "",
    "category": "Contabilidad",
    "summary": "Seguridad de Diarios Usuarios Restringidos Restricciones de Diarios Restricción de Creación de Diarios Restricción de Acceso a Diarios Control de Acceso a Diarios Restricción Base de Diarios Acceso de Usuario a Diarios Control de Acceso de Usuario Restricción de Usuario en Diarios Sistema de Restricción de Acceso a Diarios Configuración de Permisos de Usuario en Diarios Características de Restricción de Usuario en Diarios Odoo",
    "description": """Este módulo restringe diarios para usuarios específicos. Puede agregar usuarios con acceso en la configuración del diario, solo los usuarios permitidos pueden acceder a ese diario. Los usuarios se asignan a diarios específicos como facturas, facturas de proveedor, efectivo, banco, ventas y compras. Los usuarios no pueden acceder a un diario donde el diario no esté disponible para ese usuario.""",
    "version": "0.0.2",
    "depends": [
        "account"
    ],
    "application": True,
    "data": [

        "security/journal_restrict_security.xml",
        "views/account_views.xml",
        "views/res_config_settings_views.xml",

    ],

    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True
}
