{
    'name': 'Digitux Inventario',
    'version': '1.0',
    'summary': 'Control de stock en tiempo real',
    'depends': ['base', 'stock', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/digitux_stock_control_views.xml',
    ],
    'installable': True,
    'application': True,
}
