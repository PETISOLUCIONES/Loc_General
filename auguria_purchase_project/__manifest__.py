# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Auguria (<https://www.auguria.fr>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    'name': 'Auguria Purchase Project',
    'version': '17.0.0.1',
    'author': 'Auguria SAS',
    'license': 'LGPL-3',
    'summary': 'Auguria Purchase Project',
    'sequence': 15,
    'description': """
            This module allows you to create a purchase request directly from the project form.
            Another functionality is to automatically pass the analytical account to the purchase lines.
    """,
    'category': '',
    'website': 'https://www.auguria.fr/',
    'images': ['static/description/banner.png'],
    'depends': [
        'project', 'base', 'purchase',
    ],
    'data': [
        'views/project_project.xml',
        'views/purchase_order.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
