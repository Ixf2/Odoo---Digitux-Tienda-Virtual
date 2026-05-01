from odoo import http
from odoo.http import request


class GymPortalController(http.Controller):

    @http.route('/gym/schedule', type='http', auth='public', website=True)
    def public_schedule(self):
        """
        Ruta pública: cualquier visitante puede ver el horario.
        auth='public' → no requiere login.
        """
        # Recuperamos todos los horarios ordenados por día y hora
        schedules = request.env['gym.schedule'].sudo().search(
            [],
            order='day_of_week, time_start',
        )

        # Agrupamos por día para facilitar el renderizado
        days = {
            '0': 'Lunes', '1': 'Martes', '2': 'Miércoles',
            '3': 'Jueves', '4': 'Viernes', '5': 'Sábado', '6': 'Domingo',
        }
        schedule_by_day = {}
        for slot in schedules:
            day_label = days.get(slot.day_of_week, slot.day_of_week)
            schedule_by_day.setdefault(day_label, []).append(slot)

        return request.render(
            'gym_addon.portal_schedule_public',
            {
                'schedule_by_day': schedule_by_day,
                'days_order': list(days.values()),
            },
        )
