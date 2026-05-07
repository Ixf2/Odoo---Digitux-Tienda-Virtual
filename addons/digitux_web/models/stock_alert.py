# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DigituxStockAlert(models.Model):
    _name = "digitux.stock.alert"
    _description = "Alerta de stock Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "state, priority desc, create_date desc"

    name = fields.Char(string="Nombre", compute="_compute_name", store=True)
    product_id = fields.Many2one("product.product", string="Producto", required=True, tracking=True)
    min_qty = fields.Float(string="Stock mínimo", default=5.0, tracking=True)
    qty_to_order = fields.Float(string="Cantidad a pedir", default=10.0, tracking=True)
    current_qty = fields.Float(string="Stock actual", related="product_id.qty_available", readonly=True)
    vendor_id = fields.Many2one("res.partner", string="Proveedor", domain="[('supplier_rank', '>', 0)]")
    purchase_order_id = fields.Many2one("purchase.order", string="RFQ generada", readonly=True, copy=False)
    priority = fields.Selection(
        selection=[("0", "Baja"), ("1", "Normal"), ("2", "Alta"), ("3", "Crítica")],
        string="Prioridad",
        default="1",
    )
    state = fields.Selection(
        selection=[("watching", "Vigilando"), ("purchase_created", "RFQ creada"), ("closed", "Cerrada")],
        string="Estado",
        default="watching",
        tracking=True,
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    @api.depends("product_id", "min_qty")
    def _compute_name(self):
        for alert in self:
            alert.name = _("%s bajo %s uds") % (alert.product_id.display_name or _("Producto"), alert.min_qty or 0)

    def action_create_purchase_order(self):
        for alert in self:
            if alert.purchase_order_id:
                continue
            vendor = alert.vendor_id or alert.product_id.product_tmpl_id.seller_ids[:1].partner_id
            if not vendor:
                raise UserError(_("Define un proveedor en la alerta o en la ficha del producto."))
            order = self.env["purchase.order"].create({
                "partner_id": vendor.id,
                "origin": alert.name,
                "company_id": alert.company_id.id,
            })
            self.env["purchase.order.line"].create({
                "order_id": order.id,
                "product_id": alert.product_id.id,
                "name": alert.product_id.display_name,
                "product_qty": alert.qty_to_order,
                "product_uom": alert.product_id.uom_po_id.id,
                "price_unit": alert.product_id.standard_price or 0.0,
                "date_planned": fields.Datetime.now(),
            })
            alert.write({"purchase_order_id": order.id, "state": "purchase_created"})
        return True

    def action_close(self):
        self.write({"state": "closed"})

    def action_watch(self):
        self.write({"state": "watching"})
