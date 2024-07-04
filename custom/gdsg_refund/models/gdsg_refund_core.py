from odoo import models, fields, api, tools, _


class Refund_Core(models.Model):
    _name = 'gdsg_refund.core'
    _description = 'Refund Core'

    name = fields.Char('Title', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract', required=True)
    transaction_id = fields.Many2one('gdsg_contract.transaction', string='Revenue', required=True)
    refund_period = fields.Char('Refund period', required=True)
    structure_id = fields.Many2one('gdsg_refund.structure', string='Structure', required=True)
    description = fields.Char('Description')
    lesson = fields.Integer('Lesson')
    refund_school = fields.Integer('School percent')
    refund_company = fields.Integer('Company percent')
    material_price = fields.Integer('Material price')
    tuition_price = fields.Integer('Tuition price')
    refund_line = fields.One2many('gdsg_refund.core.lines', 'refund_core_id')

    def generate_data(self):
        self.name = "NEW1233445"

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gdsg_refund.core') or _('New')
        res = super(Refund_Core, self).create(vals)
        return res

class Refund_Core_Line(models.Model):
    _name = 'gdsg_refund.core.lines'
    _description = 'Refund Core Lines'

    refund_core_id = fields.Many2one('gdsg_refund.core', string='Refund Line', required=True)
    rule_id = fields.Many2one('gdsg_refund.rule', string='Rule')
    category_id = fields.Many2one('gdsg_refund.rule.category', string='Category')
    amount = fields.Float('Amount')
    note = fields.Char('Note')



