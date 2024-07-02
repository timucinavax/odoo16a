from odoo import models, fields, api, tools, _


class Refund_Rule_Category(models.Model):
    _name = 'gdsg_refund.rule.category'
    _description = 'Refund Rule Category'

    name = fields.Char('Title', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Char('Description')
