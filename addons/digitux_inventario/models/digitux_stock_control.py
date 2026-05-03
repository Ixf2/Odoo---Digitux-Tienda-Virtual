from odoo import models, fields

class DigituxStockControl(models.Model):
    _name = 'digitux.stock.control'
    _description = 'Control de Stock Digitux'

    name = fields.Char(string='Referencia', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    location_id = fields.Many2one('stock.location', string='Ubicación')
    current_stock = fields.Float(string='Stock Actual', related='product_id.qty_available', readonly=True)
    last_check_date = fields.Datetime(string='Última Verificación', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('verified', 'Verificado'),
        ('issue', 'Discrepancia')
    ], string='Estado', default='draft')
    notes = fields.Text(string='Notas')
