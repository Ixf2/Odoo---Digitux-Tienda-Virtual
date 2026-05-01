{
    'name': 'Digitux Ventas',
    'version': '1.0',
    'summary': 'Gestión de ventas de Digitux',
    'depends': ['base', 'sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/digitus_sale_views.xml',
    ],
    'installable': True,
    'application': True,
}
