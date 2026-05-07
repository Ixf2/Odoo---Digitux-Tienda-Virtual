# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class DigituxCustomerPortal(CustomerPortal):
    def _digitux_partner_domain(self):
        partner = request.env.user.partner_id.commercial_partner_id
        return [("partner_id", "child_of", [partner.id])]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "digitux_rma_count" in counters:
            values["digitux_rma_count"] = request.env["digitux.rma.request"].sudo().search_count(self._digitux_partner_domain())
        if "digitux_build_count" in counters:
            values["digitux_build_count"] = request.env["digitux.pc.build"].sudo().search_count(self._digitux_partner_domain())
        if "digitux_followup_count" in counters:
            values["digitux_followup_count"] = request.env["digitux.sale.followup"].sudo().search_count(self._digitux_partner_domain())
        if "digitux_purchase_request_count" in counters:
            values["digitux_purchase_request_count"] = request.env["digitux.purchase.request"].sudo().search_count(self._digitux_partner_domain())
        if "digitux_ticket_count" in counters:
            values["digitux_ticket_count"] = request.env["digitux.crm.ticket"].sudo().search_count([("customer_id", "child_of", [request.env.user.partner_id.commercial_partner_id.id])])
        return values

    @http.route(["/my/digitux"], type="http", auth="user", website=True)
    def dashboard(self, **kw):
        ticket_domain = [("customer_id", "child_of", [request.env.user.partner_id.commercial_partner_id.id])]
        rmas = request.env["digitux.rma.request"].sudo().search(self._digitux_partner_domain(), limit=10)
        builds = request.env["digitux.pc.build"].sudo().search(self._digitux_partner_domain(), limit=10)
        followups = request.env["digitux.sale.followup"].sudo().search(self._digitux_partner_domain(), limit=10)
        purchase_requests = request.env["digitux.purchase.request"].sudo().search(self._digitux_partner_domain(), limit=10)
        tickets = request.env["digitux.crm.ticket"].sudo().search(ticket_domain, limit=10)
        dashboard_counts = {
            "builds": request.env["digitux.pc.build"].sudo().search_count(self._digitux_partner_domain()),
            "rmas": request.env["digitux.rma.request"].sudo().search_count(self._digitux_partner_domain()),
            "followups": request.env["digitux.sale.followup"].sudo().search_count(self._digitux_partner_domain()),
            "purchase_requests": request.env["digitux.purchase.request"].sudo().search_count(self._digitux_partner_domain()),
            "tickets": request.env["digitux.crm.ticket"].sudo().search_count(ticket_domain),
        }
        return request.render("digitux_web.portal_dashboard", {
            "rmas": rmas,
            "builds": builds,
            "followups": followups,
            "purchase_requests": purchase_requests,
            "tickets": tickets,
            "dashboard_counts": dashboard_counts,
            "page_name": "digitux_portal",
        })

    @http.route(["/my/digitux/rma/<int:rma_id>"], type="http", auth="user", website=True)
    def rma_detail(self, rma_id, **kw):
        rma = request.env["digitux.rma.request"].sudo().search([("id", "=", rma_id)] + self._digitux_partner_domain(), limit=1)
        if not rma:
            return request.redirect("/my/digitux")
        return request.render("digitux_web.portal_rma_detail", {"rma": rma, "page_name": "digitux_portal_rma"})

    @http.route(["/my/digitux/configuracion/<int:build_id>"], type="http", auth="user", website=True)
    def build_detail(self, build_id, **kw):
        build = request.env["digitux.pc.build"].sudo().search([("id", "=", build_id)] + self._digitux_partner_domain(), limit=1)
        if not build:
            return request.redirect("/my/digitux")
        return request.render("digitux_web.portal_build_detail", {"build": build, "page_name": "digitux_portal_build"})

    @http.route(["/my/digitux/compras"], type="http", auth="user", website=True)
    def purchase_requests(self, **kw):
        purchase_requests = request.env["digitux.purchase.request"].sudo().search(self._digitux_partner_domain(), limit=50)
        return request.render("digitux_web.portal_purchase_requests", {
            "purchase_requests": purchase_requests,
            "page_name": "digitux_portal_purchase_requests",
        })

    @http.route(["/my/digitux/seguimientos"], type="http", auth="user", website=True)
    def followups(self, **kw):
        followups = request.env["digitux.sale.followup"].sudo().search(
            self._digitux_partner_domain(),
            order="contact_date desc, id desc",
            limit=50,
        )
        return request.render("digitux_web.portal_followups", {
            "followups": followups,
            "page_name": "digitux_portal_followups",
        })

    @http.route(["/my/digitux/compra/<int:request_id>"], type="http", auth="user", website=True)
    def purchase_request_detail(self, request_id, **kw):
        request_record = request.env["digitux.purchase.request"].sudo().search([("id", "=", request_id)] + self._digitux_partner_domain(), limit=1)
        if not request_record:
            return request.redirect("/my/digitux/compras")
        return request.render("digitux_web.portal_purchase_request_detail", {
            "request_record": request_record,
            "page_name": "digitux_portal_purchase_request",
        })

    @http.route(["/my/digitux/tickets"], type="http", auth="user", website=True)
    def tickets(self, **kw):
        ticket_domain = [("customer_id", "child_of", [request.env.user.partner_id.commercial_partner_id.id])]
        tickets = request.env["digitux.crm.ticket"].sudo().search(ticket_domain, limit=50)
        return request.render("digitux_web.portal_tickets", {
            "tickets": tickets,
            "page_name": "digitux_portal_tickets",
        })

    @http.route(["/my/digitux/ticket/<int:ticket_id>"], type="http", auth="user", website=True)
    def ticket_detail(self, ticket_id, **kw):
        ticket = request.env["digitux.crm.ticket"].sudo().search([
            ("id", "=", ticket_id),
            ("customer_id", "child_of", [request.env.user.partner_id.commercial_partner_id.id]),
        ], limit=1)
        if not ticket:
            return request.redirect("/my/digitux/tickets")
        return request.render("digitux_web.portal_ticket_detail", {
            "ticket": ticket,
            "page_name": "digitux_portal_ticket",
        })
