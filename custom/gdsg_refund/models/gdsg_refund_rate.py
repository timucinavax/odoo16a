from odoo import models, fields, api, tools, _


class Refund_Rate(models.Model):
    _name = 'gdsg_refund.rate'
    _description = 'Refund Rate'

    name = fields.Char('Customer', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract')
    contract_tuition = fields.Char('Contract Tuition')
    tuition_fee = fields.Integer('Tuition')
    material = fields.Integer('Material')
    total_amount = fields.Integer('Total')
    description = fields.Char('Description')
    retains = fields.Integer('Retains')
    refund_rate = fields.Integer('Refund rate (%)')
    assistant_support = fields.Integer('Assistant Support')
    teacher_remuneration = fields.Integer('Teacher remuneration')
    outside = fields.Integer('Outside')
    tax = fields.Integer('Tax (%)')



