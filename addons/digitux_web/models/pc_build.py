# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class DigituxPcBuild(models.Model):
    _name = "digitux.pc.build"
    _description = "Configuración PC Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Referencia", default=lambda self: _("Nuevo"), copy=False, readonly=True)
    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    email = fields.Char(string="Email", related="partner_id.email", readonly=True)
    phone = fields.Char(string="Teléfono", related="partner_id.phone", readonly=True)
    line_ids = fields.One2many("digitux.pc.build.line", "build_id", string="Componentes")
    sale_order_id = fields.Many2one("sale.order", string="Presupuesto", readonly=True, copy=False)
    crm_lead_id = fields.Many2one("crm.lead", string="Oportunidad CRM", readonly=True, copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("quoted", "Presupuestado"),
            ("won", "Ganado"),
            ("cancel", "Cancelado"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    use_case = fields.Selection(
        selection=[
            ("gaming", "Gaming"),
            ("office", "Oficina/estudio"),
            ("design", "Diseño/edición"),
            ("ai", "IA/desarrollo"),
        ],
        string="Uso previsto",
        default="gaming",
    )
    notes = fields.Text(string="Notas del cliente")
    total_amount = fields.Monetary(string="Total estimado", compute="_compute_total", store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, required=True)
    compatibility_score = fields.Integer(string="Compatibilidad %", compute="_compute_compatibility", store=True)
    compatibility_notes = fields.Text(string="Diagnóstico de compatibilidad", compute="_compute_compatibility", store=True)
    recommended_power_watts = fields.Integer(string="Fuente recomendada W", compute="_compute_compatibility", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code("digitux.pc.build") or _("Nuevo")
        return super().create(vals_list)

    def _compute_access_url(self):
        super()._compute_access_url()
        for build in self:
            build.access_url = "/my/digitux/configuracion/%s" % build.id

    @api.depends("line_ids.subtotal")
    def _compute_total(self):
        for build in self:
            build.total_amount = sum(build.line_ids.mapped("subtotal"))

    @api.depends(
        "line_ids.product_id",
        "line_ids.product_id.product_tmpl_id.digitux_socket",
        "line_ids.product_id.product_tmpl_id.digitux_ram_type",
        "line_ids.product_id.product_tmpl_id.digitux_power_watts",
        "line_ids.product_id.product_tmpl_id.digitux_component_type",
    )
    def _compute_compatibility(self):
        for build in self:
            notes = []
            score = 100 if build.line_ids else 0
            components = {}
            for line in build.line_ids:
                ctype = line.component_type
                if ctype and ctype not in components:
                    components[ctype] = line.product_id

            cpu = components.get("cpu")
            motherboard = components.get("motherboard")
            ram = components.get("ram")
            psu = components.get("psu")

            if cpu and motherboard:
                cpu_socket = cpu.product_tmpl_id.digitux_socket
                board_socket = motherboard.product_tmpl_id.digitux_socket
                if cpu_socket and board_socket and cpu_socket.lower() == board_socket.lower():
                    notes.append(_("CPU y placa base compatibles: socket %s.") % cpu_socket)
                else:
                    score -= 35
                    notes.append(_("Revisar socket: CPU %s / placa %s.") % (cpu_socket or "?", board_socket or "?"))
            elif build.line_ids:
                score -= 10
                notes.append(_("Falta CPU o placa base para comprobar socket."))

            if ram and motherboard:
                ram_type = ram.product_tmpl_id.digitux_ram_type
                board_ram = motherboard.product_tmpl_id.digitux_ram_type
                if ram_type and board_ram and ram_type == board_ram:
                    notes.append(_("RAM compatible con placa: %s.") % ram_type.upper())
                else:
                    score -= 25
                    notes.append(_("Revisar RAM: módulo %s / placa %s.") % (ram_type or "?", board_ram or "?"))

            total_consumption = sum(
                line.product_id.product_tmpl_id.digitux_power_watts or 0
                for line in build.line_ids
                if line.component_type in ("cpu", "gpu", "storage", "cooler")
            )
            recommended = int(total_consumption * 1.35) if total_consumption else 0
            if psu and recommended:
                psu_watts = psu.product_tmpl_id.digitux_power_watts or 0
                if psu_watts >= recommended:
                    notes.append(_("Fuente suficiente: %sW para recomendación de %sW.") % (psu_watts, recommended))
                else:
                    score -= 20
                    notes.append(_("Fuente insuficiente: %sW; recomendado mínimo %sW.") % (psu_watts, recommended))
            elif recommended:
                score -= 10
                notes.append(_("Falta seleccionar fuente de alimentación."))

            if not build.line_ids:
                notes.append(_("Añade componentes para calcular compatibilidad."))

            build.compatibility_score = max(score, 0)
            build.compatibility_notes = "\n".join(notes)
            build.recommended_power_watts = recommended

    def create_sale_order(self):
        self.ensure_one()
        if self.sale_order_id:
            return self.sale_order_id
        if not self.line_ids:
            raise UserError(_("Añade al menos un componente para crear el presupuesto."))
        order = self.env["sale.order"].create({
            "partner_id": self.partner_id.id,
            "origin": self.name,
            "client_order_ref": self.name,
            "note": _("Presupuesto generado por el configurador web Digitux. Compatibilidad: %s%%\n%s")
            % (self.compatibility_score, self.compatibility_notes or ""),
        })
        for line in self.line_ids:
            self.env["sale.order.line"].create({
                "order_id": order.id,
                "product_id": line.product_id.id,
                "product_uom_qty": line.quantity,
                "product_uom": line.product_id.uom_id.id,
                "price_unit": line.unit_price,
                "name": line.product_id.display_name,
            })
        self.write({"sale_order_id": order.id, "state": "quoted"})
        self.message_post(body=_("Presupuesto %s creado automáticamente.") % order.name)
        return order

    def create_crm_lead(self):
        self.ensure_one()
        if self.crm_lead_id:
            return self.crm_lead_id
        lead = self.env["crm.lead"].create({
            "name": _("Configuración PC %s") % self.name,
            "partner_id": self.partner_id.id,
            "email_from": self.partner_id.email,
            "phone": self.partner_id.phone,
            "type": "opportunity",
            "expected_revenue": self.total_amount,
            "description": _("Solicitud web Digitux.\nUso: %s\nCompatibilidad: %s%%\n%s")
            % (self.use_case or "", self.compatibility_score, self.compatibility_notes or ""),
        })
        self.crm_lead_id = lead.id
        return lead

    def action_create_sale_order(self):
        order = self.create_sale_order()
        return {"type": "ir.actions.act_window", "name": _("Presupuesto"), "res_model": "sale.order", "res_id": order.id, "view_mode": "form"}

    def action_create_crm_lead(self):
        lead = self.create_crm_lead()
        return {"type": "ir.actions.act_window", "name": _("Oportunidad CRM"), "res_model": "crm.lead", "res_id": lead.id, "view_mode": "form"}

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_reset_draft(self):
        self.write({"state": "draft"})


class DigituxPcBuildLine(models.Model):
    _name = "digitux.pc.build.line"
    _description = "Línea de configuración PC Digitux"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    build_id = fields.Many2one("digitux.pc.build", string="Configuración", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        required=True,
        domain="[('sale_ok', '=', True), ('product_tmpl_id.digitux_is_component', '=', True)]",
    )
    component_type = fields.Selection(related="product_id.product_tmpl_id.digitux_component_type", store=True, readonly=True)
    quantity = fields.Float(string="Cantidad", default=1.0)
    unit_price = fields.Monetary(string="Precio unitario")
    subtotal = fields.Monetary(string="Subtotal", compute="_compute_subtotal", store=True)
    currency_id = fields.Many2one(related="build_id.currency_id", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("product_id") and not vals.get("unit_price"):
                product = self.env["product.product"].browse(vals["product_id"])
                vals["unit_price"] = product.lst_price
        return super().create(vals_list)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.product_id:
                line.unit_price = line.product_id.lst_price

    @api.depends("quantity", "unit_price")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
