from odoo import models, fields

class DigitusCrmTicket(models.Model):
    _name = 'digitus.crm.ticket'
    _description = 'Ticket de Atención CRM Digitus'

    name = fields.Char(string='Asunto', required=True)
    customer_id = fields.Many2one('res.partner', string='Cliente', required=True)
    state = fields.Selection([
        ('open', 'Abierto'), ('closed', 'Cerrado')
    ], string='Estado', default='open')