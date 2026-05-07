# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class DigituxPriceAlert(models.Model):
    _name = "digitux.price.alert"
    _description = "Alerta de precio Digitux"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(string="Referencia", compute="_compute_name", store=True)
    partner_id = fields.Many2one("res.partner", string="Cliente", required=True, tracking=True)
    email = fields.Char(string="Email", required=True, tracking=True)
    product_id = fields.Many2one("product.product", string="Producto", required=True, tracking=True)
    current_price = fields.Float(string="Precio actual", related="product_id.lst_price", readonly=True)
    target_price = fields.Monetary(string="Precio objetivo", required=True, tracking=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id, required=True)
    state = fields.Selection(
        selection=[("active", "Activa"), ("notified", "Notificada"), ("cancel", "Cancelada")],
        string="Estado",
        default="active",
        tracking=True,
    )
    note = fields.Text(string="Notas")

    @api.depends("product_id", "target_price")
    def _compute_name(self):
        for alert in self:
            alert.name = _("Alerta %s <= %s") % (alert.product_id.display_name or _("Producto"), alert.target_price or 0)

    def action_mark_notified(self):
        self.write({"state": "notified"})

    def action_cancel(self):
        self.write({"state": "cancel"})
