{
    'name': 'Job Invoice DIAN',
    'version': '1.0',
    'summary': 'Enviar facturas a la DIAN por trabajos',
    'description': 'Enviar facturas a la DIAN por trabajos.',
    'author': 'PETI SOLUCIONES PRODUCTIVAS S.A.S',
    'depends': ['facturacion_electronica', 'queue_job'],
    'data': [
        'data/ir_cron_data.xml',
    ],
    'installable': True,
}
