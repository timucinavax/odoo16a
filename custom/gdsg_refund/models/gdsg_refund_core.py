from odoo import models, fields, api, tools, _


class Refund_Core(models.Model):
    _name = 'gdsg_refund.core'
    _description = 'Refund Core'

    name = fields.Char('Customer', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract')
    refund_period = fields.Char('Refund period')
    structure_id = fields.Many2one('gdsg_refund.structure', string='Structure')
    description = fields.Char('Description')
    lesson = fields.Integer('Lesson')
    refund_school = fields.Integer('School percent')
    refund_company = fields.Integer('Company percent')
    material_price = fields.Integer('Material price')
    tuition_price = fields.Integer('Tuition price')
    refund_line = fields.One2many('gdsg_refund.core.lines', 'ref')


class Refund_Core_Line(models.Model):
    _name = 'gdsg_refund.core.lines'
    _description = 'Refund Core Lines'

    ref = fields.Many2one('gdsg.material.management', string='Chi tiết')
    name = fields.Char('Tiêu đề', required=True)
    duration = fields.Datetime('Thời gian')
    type = fields.Selection([('pdf', 'pdf'), ('ppt', 'ppt'), ('doc', 'doc')],
                            required=True, default='pdf')
    attachment = fields.Binary('File đính kèm', help="File to check and/or import, raw binary (not base64)")



