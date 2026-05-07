# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DigituxPurchaseRequest(models.Model):
    _name = "digitux.purchase.request"
    _description = "Solicitud de compra Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Referencia", required=True, copy=False, default=lambda self: _("Nuevo"), readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Solicitante",
        required=True,
        tracking=True,
        default=lambda self: self.env.user.partner_id,
    )
    email = fields.Char(string="Email", related="partner_id.email", readonly=True)
    supplier_id = fields.Many2one("res.partner", string="Proveedor", domain="[('supplier_rank', '>', 0)]", tracking=True)
    purchase_order_id = fields.Many2one("purchase.order", string="Orden de compra", readonly=True, copy=False)
    product_id = fields.Many2one("product.product", string="Producto principal")
    quantity = fields.Float(string="Cantidad", default=1.0)
    estimated_price = fields.Monetary(string="Precio estimado")
    total_estimated = fields.Monetary(string="Total estimado", compute="_compute_total", store=True)
    required_date = fields.Date(string="Fecha requerida")
    notes = fields.Text(string="Notas")
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("confirmed", "Confirmada"),
            ("purchased", "Comprada"),
            ("cancelled", "Cancelada"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code("digitux.purchase.request") or _("Nuevo")
        return super().create(vals_list)

    def _compute_access_url(self):
        super()._compute_access_url()
        for request_record in self:
            request_record.access_url = "/my/digitux/compra/%s" % request_record.id

    @api.depends("quantity", "estimated_price")
    def _compute_total(self):
        for request_record in self:
            request_record.total_estimated = request_record.quantity * request_record.estimated_price

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset_draft(self):
        self.write({"state": "draft"})

    def action_create_purchase_order(self):
        self.ensure_one()
        if self.purchase_order_id:
            return self.action_view_purchase_order()
        if not self.supplier_id:
            raise UserError(_("Debes seleccionar un proveedor."))
        line_vals = []
        if self.product_id:
            line_vals.append((0, 0, {
                "product_id": self.product_id.id,
                "name": self.product_id.display_name,
                "product_qty": self.quantity,
                "price_unit": self.estimated_price,
                "product_uom": self.product_id.uom_po_id.id or self.product_id.uom_id.id,
                "date_planned": self.required_date or fields.Datetime.now(),
            }))
        purchase_order = self.env["purchase.order"].create({
            "partner_id": self.supplier_id.id,
            "origin": self.name,
            "company_id": self.company_id.id,
            "order_line": line_vals,
        })
        self.write({"purchase_order_id": purchase_order.id, "state": "purchased"})
        return self.action_view_purchase_order()

    def action_view_purchase_order(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Orden de compra"),
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": self.purchase_order_id.id,
        }
