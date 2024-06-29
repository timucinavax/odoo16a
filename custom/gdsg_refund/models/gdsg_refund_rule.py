from odoo import models, fields, api, tools, _


class Refund_Rule(models.Model):
    _name = 'gdsg_refund.rule'
    _description = 'Refund Rule'

    name = fields.Char('Title', required=True)
    code = fields.Char('Code', required=True)
    active = fields.Boolean('Active')
    sequence = fields.Integer('Sequence')
    category_id = fields.Many2one('gdsg_refund.rule.category','Rule Category')
    python_code = fields.Text('Python Code')
