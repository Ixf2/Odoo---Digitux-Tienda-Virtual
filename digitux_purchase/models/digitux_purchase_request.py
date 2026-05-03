from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DigituxPurchaseRequest(models.Model):
    _name = 'digitux.purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Solicitud de Compra Digitux'

    name = fields.Char(
        string='Referencia',
        required=True,
        copy=False,
        default='Nuevo',
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('purchased', 'Comprada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', tracking=True)

    supplier_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        domain=[('supplier_rank', '>', 0)]
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Orden de compra',
        readonly=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto principal'
    )
    quantity = fields.Float(string='Cantidad', default=1.0)
    estimated_price = fields.Float(string='Precio estimado')
    total_estimated = fields.Float(
        string='Total estimado',
        compute='_compute_total',
        store=True
    )
    required_date = fields.Date(string='Fecha requerida')
    notes = fields.Text(string='Notas')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('digitux.purchase.request') or 'Nuevo'
        return super().create(vals_list)

    @api.depends('quantity', 'estimated_price')
    def _compute_total(self):
        for r in self:
            r.total_estimated = r.quantity * r.estimated_price

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_create_purchase_order(self):
        self.ensure_one()
        if not self.supplier_id:
            raise UserError(_('Debe seleccionar un proveedor.'))
        line_vals = []
        if self.product_id:
            line_vals.append((0, 0, {
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'product_qty': self.quantity,
                'price_unit': self.estimated_price,
                'product_uom': self.product_id.uom_po_id.id or self.product_id.uom_id.id,
                'date_planned': self.required_date or fields.Date.today(),
            }))
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier_id.id,
            'origin': self.name,
            'order_line': line_vals,
        })
        self.write({'purchase_order_id': po.id, 'state': 'purchased'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': po.id,
        }

    def action_view_purchase_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'res_id': self.purchase_order_id.id,
        }
