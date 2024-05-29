from odoo import models, fields, api, tools, _


class Material_Management(models.Model):
    _name = 'gdsg.material.management'
    _description = 'Material Management'

    name = fields.Char('Tiêu đề', required=True)
    active_date = fields.Datetime('Ngày hiệu lực')
    pic = fields.Many2one('res.partner','Người phụ trách')
    description = fields.Char('Diễn giải')
    balance = fields.Integer('Số lượng tồn', default=0)
    type = fields.Selection([('pdf', 'pdf'), ('ppt', 'ppt'), ('doc', 'doc')],
                            required=True, default='pdf')
    attachment = fields.Binary('File đính kèm', help="File to check and/or import, raw binary (not base64)")
    material_line = fields.One2many('gdsg.material.management.line', 'ref')

class Material_Management_Line(models.Model):
    _name = 'gdsg.material.management.line'
    _description = 'Material Management Line'

    ref = fields.Many2one('gdsg.material.management', string='Chi tiết')
    name = fields.Char('Tiêu đề', required=True)
    duration = fields.Datetime('Thời gian')
    type = fields.Selection([('pdf', 'pdf'),('ppt', 'ppt'),('doc', 'doc')],
                                    required=True, default='pdf')
    attachment = fields.Binary('File đính kèm', help="File to check and/or import, raw binary (not base64)")