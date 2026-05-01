from odoo import models, fields


class GymActivity(models.Model):
    _name = 'gym.activity'
    _description = 'Actividad del gimnasio'

    name = fields.Char(
        string='Nombre',
        required=True,
    )
    description = fields.Text(
        string='Descripción',
    )
    max_capacity = fields.Integer(
        string='Capacidad máxima',
        default=20,
    )
    duration = fields.Float(
        string='Duración (horas)',
        default=1.0,
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )

    # ── NUEVO en paso 2 ──────────────────────────────────────────
    # Relación inversa: desde la actividad vemos todos sus horarios
    schedule_ids = fields.One2many(
        comodel_name='gym.schedule',
        inverse_name='activity_id',
        string='Horarios',
    )
