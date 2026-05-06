{
    'name': 'Digitux Gestión de Compras',
    'version': '19.0.1.0.0',
    'summary': 'Gestión de solicitudes de compra para Digitux',
    'author': 'Digitux',
    'category': 'Purchase',
    'depends': ['purchase', 'portal', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/digitux_purchase_sequence.xml',
        'views/digitux_purchase_request_views.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
