# -*- coding: utf-8 -*-

from odoo import _, fields, http
from odoo.http import request


class DigituxWebsiteController(http.Controller):
    COMPONENT_TYPES = [
        ("cpu", "Procesador"),
        ("cooler", "Refrigeracion"),
        ("motherboard", "Placa base"),
        ("ram", "Memoria RAM"),
        ("gpu", "Tarjeta grafica"),
        ("storage", "Almacenamiento"),
        ("psu", "Fuente"),
        ("case", "Caja"),
        ("monitor", "Monitor"),
        ("keyboard", "Teclado"),
        ("mouse", "Raton"),
        ("accessory", "Accesorio"),
    ]
    # Cada familia apunta a una imagen local para que la home y la tienda no dependan de fichas vacias.
    COMPONENT_VISUALS = {
        "cpu": "/digitux_web/static/src/img/motherboard-closeup.jpg",
        "cooler": "/digitux_web/static/src/img/motherboard-closeup.jpg",
        "motherboard": "/digitux_web/static/src/img/motherboard-closeup.jpg",
        "ram": "/digitux_web/static/src/img/motherboard-closeup.jpg",
        "gpu": "/digitux_web/static/src/img/command-center.jpg",
        "storage": "/digitux_web/static/src/img/creator-desk.jpg",
        "psu": "/digitux_web/static/src/img/motherboard-closeup.jpg",
        "case": "/digitux_web/static/src/img/command-center.jpg",
        "monitor": "/digitux_web/static/src/img/creator-desk.jpg",
        "keyboard": "/digitux_web/static/src/img/keyboard-clean.jpg",
        "mouse": "/digitux_web/static/src/img/keyboard-clean.jpg",
        "accessory": "/digitux_web/static/src/img/creator-desk.jpg",
    }

    def _component_domain(self):
        return [
            ("sale_ok", "=", True),
            ("product_tmpl_id.digitux_is_component", "=", True),
            ("product_tmpl_id.website_published", "=", True),
        ]

    def _get_products_by_type(self):
        Product = request.env["product.product"].sudo()
        return {
            key: Product.search(self._component_domain() + [("product_tmpl_id.digitux_component_type", "=", key)], limit=30)
            for key, _label in self.COMPONENT_TYPES
        }

    def _get_catalog_stats(self):
        # Estos contadores alimentan la narrativa de la portada y evitan textos fijos sin relacion con la BD.
        Product = request.env["product.product"].sudo()
        Partner = request.env["res.partner"].sudo()
        Build = request.env["digitux.pc.build"].sudo()
        Lead = request.env["crm.lead"].sudo()
        Rma = request.env["digitux.rma.request"].sudo()
        SaleOrder = request.env["sale.order"].sudo()
        PurchaseRequest = request.env["digitux.purchase.request"].sudo()
        SaleFollowup = request.env["digitux.sale.followup"].sudo()
        StockControl = request.env["digitux.stock.control"].sudo()
        Ticket = request.env["digitux.crm.ticket"].sudo()
        published_products = Product.search(self._component_domain())
        active_types = {
            product.product_tmpl_id.digitux_component_type
            for product in published_products
            if product.product_tmpl_id.digitux_component_type
        }
        prices = published_products.mapped("lst_price")
        return {
            "product_count": len(published_products),
            "component_type_count": len(active_types),
            "supplier_count": Partner.search_count([("supplier_rank", ">", 0)]),
            "entry_price": min(prices) if prices else 0.0,
            "build_count": Build.search_count([]),
            "lead_count": Lead.search_count([]),
            "rma_count": Rma.search_count([]),
            "order_count": SaleOrder.search_count([]),
            "purchase_request_count": PurchaseRequest.search_count([]),
            "sale_followup_count": SaleFollowup.search_count([]),
            "stock_control_count": StockControl.search_count([]),
            "ticket_count": Ticket.search_count([]),
        }

    def _get_component_type_counts(self):
        Product = request.env["product.product"].sudo()
        counts = []
        for key, label in self.COMPONENT_TYPES:
            count = Product.search_count(self._component_domain() + [("product_tmpl_id.digitux_component_type", "=", key)])
            if count:
                counts.append({
                    "key": key,
                    "label": label,
                    "count": count,
                })
        return counts

    def _get_home_spotlights(self):
        return [
            {
                "eyebrow": "Command center",
                "title": "Setups premium para gaming, stream y demostraciones que hacen lucir la tienda mucho mas seria.",
                "description": "Una direccion visual mas fuerte para la portada y una narrativa comercial conectada con presupuesto, CRM y cierre.",
                "image": "/digitux_web/static/src/img/command-center.jpg",
                "url": "/digitux/configurador",
                "cta": "Montar setup",
            },
            {
                "eyebrow": "Creator desks",
                "title": "Mesas limpias, monitores curvos y estaciones de trabajo para vender valor medio alto con mejor imagen.",
                "description": "La tienda no se queda en gaming: tambien vende equipos de estudio, despacho tecnico y contenido.",
                "image": "/digitux_web/static/src/img/creator-desk.jpg",
                "url": "/shop",
                "cta": "Ver catalogo",
            },
            {
                "eyebrow": "Backoffice y logistica",
                "title": "Compras, inventario, tickets y RMA visibles desde el mismo Odoo sin operativa dispersa.",
                "description": "Cada CTA de la web termina empujando un proceso util: build, pedido, ticket, compra, seguimiento o stock.",
                "image": "/digitux_web/static/src/img/logistics-aisle.jpg",
                "url": "/digitux/envio",
                "cta": "Ver logistica",
            },
        ]

    def _get_service_lanes(self):
        return [
            {
                "title": "Compatibilidad guiada",
                "description": "El configurador filtra piezas publicadas, calcula potencia recomendada y genera presupuesto comercial.",
                "image": "/digitux_web/static/src/img/motherboard-closeup.jpg",
                "url": "/digitux/configurador",
            },
            {
                "title": "Comparacion con contexto",
                "description": "La comparativa baja a socket, RAM, garantia, potencia y alertas, con una presentacion mas limpia.",
                "image": "/digitux_web/static/src/img/creator-desk.jpg",
                "url": "/digitux/comparador",
            },
            {
                "title": "Postventa visible",
                "description": "Soporte web, tickets CRM, RMA publico y seguimiento desde portal para no perder incidencias.",
                "image": "/digitux_web/static/src/img/support-headset.jpg",
                "url": "/digitux/soporte",
            },
        ]

    def _get_or_create_partner(self, post):
        user = request.env.user
        if not user._is_public():
            return user.partner_id.sudo()
        email = (post.get("email") or "").strip().lower()
        name = (post.get("name") or email or _("Cliente web Digitux")).strip()
        phone = (post.get("phone") or "").strip()
        Partner = request.env["res.partner"].sudo()
        partner = Partner.search([("email", "=", email)], limit=1) if email else Partner.browse()
        if not partner:
            partner = Partner.create({"name": name, "email": email, "phone": phone, "customer_rank": 1})
        else:
            vals = {}
            if phone and not partner.phone:
                vals["phone"] = phone
            if name and partner.name == partner.email:
                vals["name"] = name
            if vals:
                partner.write(vals)
        return partner

    @http.route(["/digitux"], type="http", auth="public", website=True, sitemap=True)
    def home(self, **kw):
        Product = request.env["product.product"].sudo()
        featured = Product.search(self._component_domain() + [("product_tmpl_id.digitux_highlight", "=", True)], limit=6)
        if len(featured) < 6:
            featured |= Product.search(self._component_domain() + [("id", "not in", featured.ids)], limit=6 - len(featured))
        return request.render("digitux_web.home", {
            "featured_products": featured,
            "catalog_stats": self._get_catalog_stats(),
            "component_type_counts": self._get_component_type_counts(),
            "home_spotlights": self._get_home_spotlights(),
            "service_lanes": self._get_service_lanes(),
            "component_visuals": self.COMPONENT_VISUALS,
            "page_name": "digitux_home",
        })

    @http.route(["/digitux/configurador"], type="http", auth="public", website=True, methods=["GET", "POST"], sitemap=True)
    def configurator(self, **post):
        if request.httprequest.method == "POST":
            partner = self._get_or_create_partner(post)
            build = request.env["digitux.pc.build"].sudo().create({
                "partner_id": partner.id,
                "use_case": post.get("use_case") or "gaming",
                "notes": post.get("notes") or "",
            })
            Product = request.env["product.product"].sudo()
            sequence = 10
            for key, _label in self.COMPONENT_TYPES:
                try:
                    product_id = int(post.get("component_%s" % key) or 0)
                except (TypeError, ValueError):
                    product_id = 0
                product = Product.browse(product_id).exists() if product_id else Product.browse()
                if product:
                    request.env["digitux.pc.build.line"].sudo().create({
                        "build_id": build.id,
                        "product_id": product.id,
                        "quantity": 1,
                        "sequence": sequence,
                    })
                    sequence += 10
            order = False
            if build.line_ids:
                order = build.create_sale_order()
            build.create_crm_lead()
            return request.render("digitux_web.configurator_success", {
                "build": build,
                "order": order,
                "page_name": "digitux_configurator_success",
            })
        return request.render("digitux_web.configurator", {
            "components": self._get_products_by_type(),
            "component_types": self.COMPONENT_TYPES,
            "page_name": "digitux_configurator",
        })

    @http.route(["/digitux/comparador"], type="http", auth="public", website=True, sitemap=True)
    def comparator(self, **kw):
        Product = request.env["product.product"].sudo()
        component_type = kw.get("component_type") or "gpu"
        all_products = Product.search(self._component_domain() + [("product_tmpl_id.digitux_component_type", "=", component_type)], limit=30)
        selected_ids = []
        for raw in request.httprequest.args.getlist("products"):
            try:
                selected_ids.append(int(raw))
            except (TypeError, ValueError):
                pass
        selected = Product.browse(selected_ids).exists() if selected_ids else all_products[:3]
        return request.render("digitux_web.comparator", {
            "component_types": self.COMPONENT_TYPES,
            "component_type": component_type,
            "all_products": all_products,
            "selected_products": selected,
            "page_name": "digitux_comparator",
        })

    @http.route(["/digitux/rma"], type="http", auth="public", website=True, methods=["GET", "POST"], sitemap=True)
    def rma(self, **post):
        Product = request.env["product.product"].sudo()
        products = Product.search(self._component_domain(), limit=80)
        if request.httprequest.method == "POST":
            try:
                product_id = int(post.get("product_id") or 0)
            except (TypeError, ValueError):
                product_id = 0
            product = Product.browse(product_id).exists() if product_id else Product.browse()
            if not product:
                return request.render("digitux_web.rma_form", {
                    "products": products,
                    "error": _("Selecciona un producto valido."),
                    "page_name": "digitux_rma",
                })
            partner = self._get_or_create_partner(post)
            order_name = (post.get("order_name") or "").strip()
            sale_order = request.env["sale.order"].sudo().search([
                ("name", "=", order_name),
                ("partner_id", "child_of", [partner.commercial_partner_id.id]),
            ], limit=1) if order_name else request.env["sale.order"].sudo().browse()
            rma = request.env["digitux.rma.request"].sudo().create({
                "partner_id": partner.id,
                "sale_order_id": sale_order.id if sale_order else False,
                "product_id": product.id,
                "fault_type": post.get("fault_type") or "other",
                "requested_solution": post.get("requested_solution") or "diagnosis",
                "courier": post.get("courier") or "gls",
                "pickup_address": post.get("pickup_address") or "",
                "description": post.get("description") or _("Sin descripcion"),
                "state": "submitted",
            })
            return request.render("digitux_web.rma_success", {"rma": rma, "page_name": "digitux_rma_success"})
        return request.render("digitux_web.rma_form", {"products": products, "error": False, "page_name": "digitux_rma"})

    @http.route(["/digitux/soporte"], type="http", auth="public", website=True, methods=["GET", "POST"], sitemap=True)
    def support(self, **post):
        values = {
            "error": False,
            "form_values": post,
            "page_name": "digitux_support",
        }
        if request.httprequest.method == "POST":
            subject = (post.get("subject") or "").strip()
            description = (post.get("description") or "").strip()
            email = (post.get("email") or "").strip()
            if not subject or not description or not email:
                values["error"] = _("Completa asunto, email y descripcion para abrir el ticket.")
                return request.render("digitux_web.support_form", values)
            partner = self._get_or_create_partner(post)
            order_name = (post.get("order_name") or "").strip()
            sale_order = request.env["sale.order"].sudo().browse()
            if order_name:
                sale_order = request.env["sale.order"].sudo().search([
                    "&",
                    ("partner_id", "child_of", [partner.commercial_partner_id.id]),
                    "|",
                    ("name", "=", order_name),
                    ("client_order_ref", "=", order_name),
                ], limit=1)
                if not sale_order:
                    values["error"] = _("No encontramos ese pedido para el email indicado.")
                    return request.render("digitux_web.support_form", values)
            priority = post.get("priority") if post.get("priority") in ("0", "1", "2") else "1"
            deadline_days = {"0": 10, "1": 5, "2": 2}[priority]
            ticket = request.env["digitux.crm.ticket"].sudo().create({
                "reference": _("Nuevo"),
                "name": subject,
                "customer_id": partner.id,
                "sale_order_id": sale_order.id if sale_order else False,
                "description": description,
                "priority": priority,
                "date_deadline": fields.Date.add(fields.Date.context_today(request.env.user), days=deadline_days),
            })
            return request.render("digitux_web.support_success", {
                "ticket": ticket,
                "page_name": "digitux_support_success",
            })
        return request.render("digitux_web.support_form", values)

    @http.route(["/digitux/alerta-precio"], type="http", auth="public", website=True, methods=["POST"], sitemap=False)
    def price_alert(self, **post):
        partner = self._get_or_create_partner(post)
        try:
            product_id = int(post.get("product_id") or 0)
        except (TypeError, ValueError):
            product_id = 0
        try:
            target_price = float((post.get("target_price") or "0").replace(",", "."))
        except (TypeError, ValueError):
            target_price = 0.0
        alert = request.env["digitux.price.alert"].sudo().create({
            "partner_id": partner.id,
            "email": partner.email or post.get("email") or "cliente@digitux.local",
            "product_id": product_id,
            "target_price": target_price,
            "note": post.get("note") or "",
        })
        return request.render("digitux_web.price_alert_success", {"alert": alert, "page_name": "digitux_price_alert_success"})

    @http.route(["/digitux/envio"], type="http", auth="public", website=True, sitemap=True)
    def shipping(self, **kw):
        carrier = kw.get("carrier") or "gls"
        zone = kw.get("zone") or "espana"
        rules = {
            ("gls", "espana"): ("24-48 horas", "2,50 EUR - 4,50 EUR", "Nacional"),
            ("gls", "europa_cercana"): ("24-48 horas", "4,50 EUR - 7,00 EUR", "Europa cercana"),
            ("gls", "europa_lejana"): ("72-96 horas", "6,00 EUR - 9,00 EUR", "Europa lejana"),
            ("dhl", "europa_lejana"): ("48-96 horas", "14,00 EUR - 20,00 EUR", "Europa lejana"),
            ("dhl", "mundial"): ("48-96 horas", "20,00 EUR - 25,00 EUR", "Mundial"),
        }
        result = rules.get((carrier, zone), rules[("gls", "espana")])
        return request.render("digitux_web.shipping", {
            "carrier": carrier,
            "zone": zone,
            "delivery_time": result[0],
            "delivery_price": result[1],
            "scope": result[2],
            "page_name": "digitux_shipping",
        })
