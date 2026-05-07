{
    "name": "Digitux Web ERP",
    "summary": "Web, configurador PC, comparador, RMA y alertas para Digitux",
    "description": """
Digitux Web ERP
================
Módulo funcional para una tienda tecnológica online: página web, configurador de PC,
comparador, gestión RMA, alertas de stock/precio e integración con ventas, compras, CRM e inventario.
    """,
    "version": "17.0.5.0.0",
    "category": "Website/Website",
    "author": "Digitux",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "portal",
        "website",
        "website_sale",
        "sale_management",
        "stock",
        "purchase",
        "crm",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequences.xml",
        "data/products.xml",
        "data/catalog_extension.xml",
        "data/website_setup.xml",
        "views/product_views.xml",
        "views/pc_build_views.xml",
        "views/rma_views.xml",
        "views/alert_views.xml",
        "views/menus.xml",
        "views/sale_followup_views.xml",
        "views/purchase_request_views.xml",
        "views/stock_control_views.xml",
        "views/crm_ticket_views.xml",
        "views/website_templates.xml",
        "views/website_refresh.xml",
        "views/website_support.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "digitux_web/static/src/css/digitux.css",
        ],
        "web.assets_backend": [
            "digitux_web/static/src/css/digitux_backend.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
