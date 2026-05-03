from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class DigituxPurchasePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'digitux_request_count' in counters:
            values['digitux_request_count'] = request.env['digitux.purchase.request'].search_count([
                ('create_uid', '=', request.env.user.id)
            ])
        return values

    @http.route(['/my/solicitudes', '/my/solicitudes/page/<int:page>'],
                type='http', auth='user', website=True)
    def portal_solicitudes(self, page=1, **kw):
        domain = [('create_uid', '=', request.env.user.id)]
        total = request.env['digitux.purchase.request'].search_count(domain)
        pager = portal_pager(url='/my/solicitudes', total=total, page=page, step=10)
        records = request.env['digitux.purchase.request'].search(
            domain, offset=pager['offset'], limit=10
        )
        return request.render('digitux_purchase.portal_my_solicitudes', {
            'purchase_requests': records,
            'pager': pager,
            'page_name': 'solicitudes',
        })
