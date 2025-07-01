# -*- coding: utf-8 -*-

{
    'name': "Diarios habilitados por usuario",
    'summary': "Diarios habilitados por usuario",
    'description': """
        Este módulo permite habilitar diarios por cada usuario.
    """,
    'author': "PETI Soluciones Productivas",
    'website': "http://peti.erp.com.co",
    'category': 'Accounting',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/groups.xml',
        'security/rules.xml',
        'views/res_config_settings.xml',
        'views/res_users.xml',
        'views/account_move.xml',
        'views/account_journal.xml',
    ],
    'sequence': 1,
    'application': True,
    'installable': True,
    'auto_install': False,
}