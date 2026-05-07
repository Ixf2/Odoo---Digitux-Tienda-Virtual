# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    digitux_is_component = fields.Boolean(
        string="Componente Digitux",
        help="Hace visible el producto en el configurador y comparador web de Digitux.",
    )
    digitux_component_type = fields.Selection(
        selection=[
            ("cpu", "Procesador"),
            ("cooler", "Refrigeración"),
            ("motherboard", "Placa base"),
            ("ram", "Memoria RAM"),
            ("gpu", "Tarjeta gráfica"),
            ("storage", "Almacenamiento"),
            ("psu", "Fuente de alimentación"),
            ("case", "Caja"),
            ("monitor", "Monitor"),
            ("keyboard", "Teclado"),
            ("mouse", "Ratón"),
            ("accessory", "Accesorio"),
        ],
        string="Tipo Digitux",
    )
    digitux_socket = fields.Char(string="Socket")
    digitux_ram_type = fields.Selection(
        selection=[
            ("ddr4", "DDR4"),
            ("ddr5", "DDR5"),
            ("na", "No aplica"),
        ],
        string="Tipo RAM",
    )
    digitux_form_factor = fields.Selection(
        selection=[
            ("atx", "ATX"),
            ("matx", "Micro-ATX"),
            ("itx", "Mini-ITX"),
            ("sfx", "SFX"),
            ("midtower", "Mid Tower"),
            ("fulltower", "Full Tower"),
            ("peripheral", "Periférico"),
            ("na", "No aplica"),
        ],
        string="Formato",
    )
    digitux_power_watts = fields.Integer(
        string="Consumo/Potencia W",
        help="En CPU/GPU indica consumo aproximado; en PSU indica potencia disponible.",
    )
    digitux_warranty_months = fields.Integer(string="Garantía meses", default=24)
    digitux_short_specs = fields.Text(string="Especificaciones web")
    digitux_highlight = fields.Boolean(string="Destacado en web Digitux")
