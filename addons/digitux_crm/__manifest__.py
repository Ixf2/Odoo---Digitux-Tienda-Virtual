{
    'name': 'Digitux CRM Base',
    'version': '1.0',
    'summary': 'Módulo base de CRM para pruebas',
    'depends': ['base', 'crm', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/digitux_crm_ticket_view.xml',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': True,
}