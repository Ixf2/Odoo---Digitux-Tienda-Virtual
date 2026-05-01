{
    'name': 'Digitux Ventas',
    'version': '1.0',
    'summary': 'Gestión de ventas de Digitux',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/digitux_sale_followup_views.xml',
    ],
    'installable': True,
    'application': True,
}
