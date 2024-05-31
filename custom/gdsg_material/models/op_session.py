from odoo import models, fields, api, tools, _


class OP_Session(models.Model):
    _inherit = ["op.session"]

    op_session_line = fields.One2many('op.session.line', 'ref')


class OP_Session_Line(models.Model):
    _name = 'op.session.line'
    _description = 'Session Line'

    ref = fields.Many2one('op.session', string='Chi tiết')
    material_id = fields.Many2one('gdsg.material.management', 'Học liệu')
    quantity = fields.Integer('Số lượng')