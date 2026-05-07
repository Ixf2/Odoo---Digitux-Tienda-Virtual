# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DigituxCrmTicket(models.Model):
    _name = "digitux.crm.ticket"
    _description = "Ticket de atencion CRM Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "priority desc, create_date desc, id desc"

    reference = fields.Char(string="Referencia", copy=False, readonly=True, default=lambda self: _("Nuevo"))
    name = fields.Char(string="Asunto", required=True, tracking=True)
    customer_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    email = fields.Char(string="Email", related="customer_id.email", readonly=True)
    phone = fields.Char(string="Telefono", related="customer_id.phone", readonly=True)
    sale_order_id = fields.Many2one("sale.order", string="Pedido relacionado")
    description = fields.Text(string="Descripcion", required=True)
    date_deadline = fields.Date(string="Fecha limite")
    priority = fields.Selection(
        selection=[("0", "Baja"), ("1", "Media"), ("2", "Alta")],
        string="Prioridad",
        default="1",
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("open", "Abierto"),
            ("in_progress", "En proceso"),
            ("closed", "Cerrado"),
        ],
        string="Estado",
        default="open",
        tracking=True,
    )
    crm_lead_id = fields.Many2one("crm.lead", string="Caso CRM", readonly=True, copy=False)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", _("Nuevo")) == _("Nuevo"):
                vals["reference"] = self.env["ir.sequence"].next_by_code("digitux.crm.ticket") or _("Nuevo")
        tickets = super().create(vals_list)
        tickets._ensure_crm_lead()
        return tickets

    def _compute_access_url(self):
        super()._compute_access_url()
        for ticket in self:
            ticket.access_url = "/my/digitux/ticket/%s" % ticket.id

    def _ensure_crm_lead(self):
        for ticket in self.filtered(lambda item: not item.crm_lead_id):
            lead = self.env["crm.lead"].create({
                "name": _("%s - %s") % (ticket.reference, ticket.name),
                "partner_id": ticket.customer_id.id,
                "email_from": ticket.customer_id.email,
                "phone": ticket.customer_id.phone,
                "type": "opportunity",
                "description": _("Ticket de soporte Digitux\nPedido: %s\nDescripcion:\n%s")
                % (ticket.sale_order_id.name or _("Sin pedido"), ticket.description),
            })
            ticket.crm_lead_id = lead.id

    def action_start_progress(self):
        self.write({"state": "in_progress"})

    def action_close(self):
        self.write({"state": "closed"})

    def action_reopen(self):
        self.write({"state": "open"})

    def action_open_crm_case(self):
        self.ensure_one()
        if not self.crm_lead_id:
            self._ensure_crm_lead()
        return {
            "type": "ir.actions.act_window",
            "name": _("Caso CRM"),
            "res_model": "crm.lead",
            "view_mode": "form",
            "res_id": self.crm_lead_id.id,
        }
