import datetime

from odoo import models, fields, api, tools, _


class Gdsg_Contract_Transaction(models.Model):
    _name = 'gdsg_contract.transaction'
    _description = 'Contract Transaction'

    name = fields.Char('Transaction No.', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract')
    type = fields.Selection([('deposit', 'Deposit'), ('withdraw', 'Withdraw')], required=True, default='Type')
    description = fields.Char('Description', required=True)
    date = fields.Datetime('Date', default=datetime.datetime.utcnow(), required=True)
    business = fields.Char('Business')
    origin = fields.Char('Origin')
    amount = fields.Float('Amount', required=True)
    move_id = fields.Char('Journal Entry')
    students_invoice = fields.Integer('Students Invoice')
    invoice_no = fields.Char('Invoice No')
    invoice_code = fields.Char('Invoice Code')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', """This transaction no has exist in system!"""),
    ]

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gdsg_contract.transaction') or _('New')
        res = super(Gdsg_Contract_Transaction, self).create(vals)
        return res

class Gdsg_Contract_Core(models.Model):
    _inherit = 'gdsg_contract.core'

    sum_revenue = fields.Float('Total revenue', compute='_compute_sum_revenue', default=0)
    sum_expense = fields.Float('Total expense', compute='_compute_sum_expense', default=0)

    # @api.depends('revenue_list')
    def _compute_sum_revenue(self):
        for rec in self:
            rec.sum_revenue = 0
            contract_transaction_list = self.env['gdsg_contract.transaction'].search([('contract_id', '=', rec.id)])
            for tran in contract_transaction_list:
                if tran.type == 'deposit':
                    # rec.revenue_list.append(tran.id)
                    rec.sum_revenue += tran.amount

    def revenue_sum_action(self):
        for rec in self:
            contract_transaction_list = self.env['gdsg_contract.transaction'].search(
                [('contract_id', '=', rec.id), ('type', '=', 'deposit')])
            return {
                "name": "Transaction",
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "views": [(False, 'tree'), (False, 'form')],
                "res_model": "gdsg_contract.transaction",
                "domain": [('id', 'in', contract_transaction_list.ids)]
            }

    # @api.depends('revenue_list')
    def _compute_sum_expense(self):
        for rec in self:
            rec.sum_expense = 0
            contract_transaction_list = self.env['gdsg_contract.transaction'].search([('contract_id', '=', rec.id)])
            for tran in contract_transaction_list:
                if tran.type == 'withdraw':
                    rec.sum_expense += tran.amount

    def expense_sum_action(self):
        for rec in self:
            contract_transaction_list = self.env['gdsg_contract.transaction'].search(
                [('contract_id', '=', rec.id), ('type', '=', 'withdraw')])
            return {
                "name": "Transaction",
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "views": [(False, 'tree'), (False, 'form')],
                "res_model": "gdsg_contract.transaction",
                "domain": [('id', 'in', contract_transaction_list.ids)]
            }