# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DigituxStockControl(models.Model):
    _name = "digitux.stock.control"
    _description = "Control de stock Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_check_date desc, id desc"

    name = fields.Char(string="Referencia", required=True, copy=False, default=lambda self: _("Nuevo"), readonly=True)
    product_id = fields.Many2one("product.product", string="Producto", required=True, tracking=True)
    location_id = fields.Many2one(
        "stock.location",
        string="Ubicacion",
        domain="[('usage', '=', 'internal')]",
        tracking=True,
    )
    current_stock = fields.Float(string="Stock actual", compute="_compute_current_stock", store=False)
    last_check_date = fields.Datetime(string="Ultima verificacion", default=fields.Datetime.now, tracking=True)
    checked_by_id = fields.Many2one("res.users", string="Revisado por", default=lambda self: self.env.user, readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("verified", "Verificado"),
            ("issue", "Discrepancia"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
    )
    notes = fields.Text(string="Notas")
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code("digitux.stock.control") or _("Nuevo")
        return super().create(vals_list)

    @api.depends("product_id", "location_id")
    def _compute_current_stock(self):
        for control in self:
            if not control.product_id:
                control.current_stock = 0.0
                continue
            product = control.product_id
            if control.location_id:
                product = product.with_context(location=control.location_id.id)
            control.current_stock = product.qty_available

    def _write_state(self, state):
        self.write({
            "state": state,
            "last_check_date": fields.Datetime.now(),
            "checked_by_id": self.env.user.id,
        })

    def action_mark_verified(self):
        self._write_state("verified")

    def action_mark_issue(self):
        self._write_state("issue")

    def action_reset_draft(self):
        self._write_state("draft")
