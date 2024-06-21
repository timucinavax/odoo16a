from odoo import models, fields, api, tools, _


class Gdsg_Contract_Core(models.Model):
    _name = 'gdsg_contract.core'
    _description = 'Contract Core'

    name = fields.Char('Số hợp đồng', required=True)
    state = fields.Selection([
        ('new', 'Mới'),
        ('process', 'Đang thực hiện'),
        ('closed', 'Đã đóng'),
        ('cancel', 'Đã hủy')
    ], readonly=True, required=True, string='Trạng thái', default='new')
    partner_id = fields.Many2one('res.partner','Khách hàng')
    represent = fields.Char('Người đại diện')
    partner_bank_id = fields.Char('Tài khoản khách hàng')
    tuition_fee = fields.Float('Học phí')
    from_date = fields.Datetime('Từ ngày')
    to_date = fields.Datetime('Đến ngày')
    description = fields.Char('Diễn giải')
