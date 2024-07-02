from odoo import models, fields, api, tools, _


class Material_Transaction(models.Model):
    _name = 'gdsg.material.transaction'
    _description = 'Material Transaction'

    material_id = fields.Many2one('gdsg.material.management', 'Học liệu')
    date = fields.Datetime('Ngày')
    partner_id = fields.Many2one('res.partner','Người phụ trách')
    description = fields.Char('Diễn giải')
    type = fields.Selection([('input', 'Nhập'),('output', 'Xuất')], required=True, default='input')
    quantity = fields.Integer('Số lượng')

    def material_balance_compute(self, record):
        material_management = self.env['gdsg.material.management'].search([('id','=',record.material_id.id)])
        total_balance = 0
        if record.type == 'input':
            total_balance = material_management.balance + record.quantity
        else:
            total_balance = material_management.balance - record.quantity
        material_management.write(dict(balance=total_balance))
        self.env.cr.commit()
