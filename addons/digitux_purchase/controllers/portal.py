from odoo import http
from odoo.http import request


class DigituxPurchasePortal(http.Controller):
    @http.route("/my/solicitudes", type="http", auth="user", website=True)
    def portal_purchase_alias(self, **kw):
        return request.redirect("/my/digitux/compras")

    @http.route("/my/solicitud/<int:request_id>", type="http", auth="user", website=True)
    def portal_purchase_detail_alias(self, request_id, **kw):
        return request.redirect("/my/digitux/compra/%s" % request_id)
