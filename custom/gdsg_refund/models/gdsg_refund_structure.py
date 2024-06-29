from odoo import models, fields, api, tools, _


class Refund_Structure(models.Model):
    _name = 'gdsg_refund.structure'
    _description = 'Refund Structure'

    name = fields.Char('Title', required=True)
    code = fields.Char('Code', required=True)
    rule_ids = fields.Many2many('gdsg_refund.rule','structure_rule_rel')
