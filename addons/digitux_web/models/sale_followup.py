# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DigituxSaleFollowup(models.Model):
    _name = "digitux.sale.followup"
    _description = "Seguimiento de ventas Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "contact_date desc, id desc"

    name = fields.Char(string="Referencia", default=lambda self: _("Nuevo"), copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    sale_order_id = fields.Many2one("sale.order", string="Pedido de venta", tracking=True)
    crm_lead_id = fields.Many2one("crm.lead", string="Oportunidad CRM", tracking=True)
    product_id = fields.Many2one("product.product", string="Producto principal")
    contact_date = fields.Date(string="Fecha de contacto", default=fields.Date.context_today, tracking=True)
    next_action_date = fields.Date(string="Proxima accion")
    notes = fields.Text(string="Notas")
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("contacted", "Cliente contactado"),
            ("quotation", "Presupuesto enviado"),
            ("won", "Venta ganada"),
            ("lost", "Venta perdida"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(related="company_id.currency_id", readonly=True)
    expected_revenue = fields.Monetary(string="Valor esperado", compute="_compute_expected_revenue", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code("digitux.sale.followup") or _("Nuevo")
        return super().create(vals_list)

    @api.depends("sale_order_id.amount_total", "product_id.lst_price")
    def _compute_expected_revenue(self):
        for record in self:
            if record.sale_order_id:
                record.expected_revenue = record.sale_order_id.amount_total
            elif record.product_id:
                record.expected_revenue = record.product_id.lst_price
            else:
                record.expected_revenue = 0.0

    def action_mark_contacted(self):
        self.write({"state": "contacted", "contact_date": fields.Date.context_today(self)})

    def action_mark_quotation(self):
        self.write({"state": "quotation"})

    def action_mark_won(self):
        self.write({"state": "won"})

    def action_mark_lost(self):
        self.write({"state": "lost"})

    def action_reset_draft(self):
        self.write({"state": "draft"})
