from odoo import http
from odoo.http import request


class DigituxVentasPortal(http.Controller):
    @http.route("/my/seguimientos", type="http", auth="user", website=True)
    def portal_sale_followups(self, **kw):
        return request.redirect("/my/digitux/seguimientos")
