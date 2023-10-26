# -*- coding: utf-8 -*-

{
    'name': 'Imprimir Asientos Contables',
    'version': '13.0',
    'category': 'account',
    'summary': 'Imprimir asiento contable',
    'description': """
    Este modulo se utiliza para generar reportes PDF de los asientos contables"
    """,
    'author': "HAK Solutions",
    'website': "http://haksolutions.com",
    'depends': ['account'],
    'license': 'AGPL-3',
    'data': [
            'report/report_menu.xml'
            ],
    "images": [
        'static/description/icon.png'
    ],
    'installable': True,
    'auto_install': False,
}
