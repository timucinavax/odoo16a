from odoo import models, fields, api, tools, _


class Gdsg_Contract_Core(models.Model):
    _name = 'gdsg_contract.core'
    _description = 'Contract Core'

    name = fields.Char('Name', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('process', 'Process'),
        ('closed', 'Closed'),
        ('cancel', 'Canceled')
    ], readonly=True, required=True, string='State', default='new')
    partner_id = fields.Many2one('res.partner', 'Partner')
    represent = fields.Char('Representative')
    partner_bank_id = fields.Many2one('res.partner.bank', string='Partner Bank', compute='_compute_res_partner_bank_id')
    tuition_fee = fields.Float('Tuition')
    from_date = fields.Datetime('From date')
    to_date = fields.Datetime('To date')
    description = fields.Text('Description')

    contract_tuition = fields.Char('Contract Tuition')
    actual_tuition = fields.Integer('Tuition')
    material = fields.Integer('Material')
    total_amount = fields.Integer('Total')
    note = fields.Char('Note')
    retains = fields.Selection([('rate', 'Rate'), ('fixed', 'Fixed')], required=True, default='rate')
    rate = fields.Integer('Rate (%)')
    fixed_amount = fields.Integer('Fixed amount')
    refund_rate = fields.Integer('Refund rate (%)')
    assistant_support = fields.Integer('Assistant Support')
    teacher_remuneration = fields.Integer('Teacher remuneration')
    outside = fields.Integer('Outside')
    tax = fields.Integer('Tax (%)')
    tuition_cit_tax = fields.Integer('CIT tax tuition')
    material_cit_tax = fields.Integer('CIT tax material')
    material_vat_tax = fields.Integer('Vat tax material')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', """This contract has exist in system!"""),
    ]

    @api.onchange('partner_id')
    def _compute_res_partner_bank_id(self):
        bank_id = self.env['res.partner.bank'].sudo().search([('partner_id', '=', self.partner_id.id)],
                                                             order='sequence')
        self.partner_bank_id = bank_id

    def action_inprocess(self):
        self.state = 'process'

    def action_close(self):
        self.state = 'closed'

    def action_cancel(self):
        self.state = 'cancel'

    def action_backtonew(self):
        self.state = 'new'
