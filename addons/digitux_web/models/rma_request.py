# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DigituxRmaRequest(models.Model):
    _name = "digitux.rma.request"
    _description = "Solicitud RMA / Garantía Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Referencia", default=lambda self: _("Nuevo"), copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    email = fields.Char(string="Email", related="partner_id.email", readonly=True)
    phone = fields.Char(string="Teléfono", related="partner_id.phone", readonly=True)
    sale_order_id = fields.Many2one("sale.order", string="Pedido relacionado")
    product_id = fields.Many2one("product.product", string="Producto", required=True)
    purchase_date = fields.Date(string="Fecha de compra", compute="_compute_purchase_date", store=True, readonly=False)
    warranty_limit_date = fields.Date(string="Fin garantía", compute="_compute_warranty", store=True)
    in_warranty = fields.Boolean(string="En garantía", compute="_compute_warranty", store=True)
    fault_type = fields.Selection(
        selection=[
            ("dead_on_arrival", "No funciona al recibirlo"),
            ("performance", "Rendimiento inferior"),
            ("physical", "Daño físico"),
            ("wrong_item", "Producto equivocado"),
            ("other", "Otro"),
        ],
        string="Tipo de incidencia",
        default="other",
        tracking=True,
    )
    requested_solution = fields.Selection(
        selection=[
            ("repair", "Reparación"),
            ("replace", "Sustitución"),
            ("refund", "Reembolso"),
            ("diagnosis", "Diagnóstico técnico"),
        ],
        string="Solución solicitada",
        default="diagnosis",
        tracking=True,
    )
    courier = fields.Selection(
        selection=[
            ("gls", "GLS Europa"),
            ("dhl", "DHL internacional"),
            ("customer", "Entrega por cliente"),
        ],
        string="Transporte preferido",
        default="gls",
    )
    pickup_address = fields.Text(string="Dirección de recogida")
    description = fields.Text(string="Descripción del problema", required=True)
    diagnostic_notes = fields.Text(string="Diagnóstico interno")
    crm_lead_id = fields.Many2one("crm.lead", string="Caso CRM", readonly=True, copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("submitted", "Enviada"),
            ("approved", "Aprobada"),
            ("received", "Producto recibido"),
            ("done", "Resuelta"),
            ("rejected", "Rechazada"),
            ("cancel", "Cancelada"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code("digitux.rma.request") or _("Nuevo")
        records = super().create(vals_list)
        for record in records:
            record._ensure_crm_case()
        return records

    def _compute_access_url(self):
        super()._compute_access_url()
        for rma in self:
            rma.access_url = "/my/digitux/rma/%s" % rma.id

    @api.depends("sale_order_id.date_order")
    def _compute_purchase_date(self):
        for rma in self:
            if rma.sale_order_id and rma.sale_order_id.date_order:
                rma.purchase_date = fields.Date.to_date(rma.sale_order_id.date_order)
            elif not rma.purchase_date:
                rma.purchase_date = fields.Date.context_today(rma)

    @api.depends("purchase_date", "product_id.product_tmpl_id.digitux_warranty_months")
    def _compute_warranty(self):
        today = fields.Date.context_today(self)
        for rma in self:
            months = rma.product_id.product_tmpl_id.digitux_warranty_months or 24
            if rma.purchase_date:
                rma.warranty_limit_date = rma.purchase_date + relativedelta(months=months)
                rma.in_warranty = rma.warranty_limit_date >= today
            else:
                rma.warranty_limit_date = False
                rma.in_warranty = False

    def _ensure_crm_case(self):
        for rma in self.filtered(lambda item: not item.crm_lead_id):
            lead = self.env["crm.lead"].create({
                "name": _("RMA %s - %s") % (rma.name, rma.product_id.display_name),
                "partner_id": rma.partner_id.id,
                "email_from": rma.partner_id.email,
                "phone": rma.partner_id.phone,
                "type": "opportunity",
                "description": _("Solicitud RMA Digitux\nProducto: %s\nPedido: %s\nTipo: %s\nSolución: %s\nDescripción:\n%s")
                % (
                    rma.product_id.display_name,
                    rma.sale_order_id.name or _("Sin pedido"),
                    rma.fault_type,
                    rma.requested_solution,
                    rma.description,
                ),
            })
            rma.crm_lead_id = lead.id

    def action_submit(self):
        for rma in self:
            if not rma.description:
                raise UserError(_("Debes incluir una descripción del problema."))
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})
        self.message_post(body=_("RMA aprobada. El cliente puede enviar o entregar el producto."))

    def action_received(self):
        self.write({"state": "received"})

    def action_done(self):
        self.write({"state": "done"})

    def action_reject(self):
        self.write({"state": "rejected"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_open_sale_order(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_("No hay pedido relacionado."))
        return {"type": "ir.actions.act_window", "name": _("Pedido"), "res_model": "sale.order", "res_id": self.sale_order_id.id, "view_mode": "form"}

    def action_open_crm_case(self):
        self.ensure_one()
        if not self.crm_lead_id:
            self._ensure_crm_case()
        return {"type": "ir.actions.act_window", "name": _("Caso CRM"), "res_model": "crm.lead", "res_id": self.crm_lead_id.id, "view_mode": "form"}
