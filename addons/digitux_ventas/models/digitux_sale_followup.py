from odoo import models, fields


class DigitusSaleFollowup(models.Model):
    _name = 'digitus.sale.followup'
    _description = 'Seguimiento de ventas Digitus'

    name = fields.Char(
        string='Referencia',
        required=True
    )

    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Pedido de venta'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto principal'
    )

    contact_date = fields.Date(
        string='Fecha de contacto'
    )

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('contacted', 'Cliente contactado'),
        ('quotation', 'Presupuesto enviado'),
        ('won', 'Venta ganada'),
        ('lost', 'Venta perdida'),
    ], string='Estado', default='draft')

    notes = fields.Text(
        string='Notas'
    )