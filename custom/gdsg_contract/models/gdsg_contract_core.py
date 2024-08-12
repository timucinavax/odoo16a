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
    partner_bank_id = fields.Many2one('res.partner.bank', string='Partner Bank', compute='_compute_res_partner_bank_id', store=True)
    tuition_fee = fields.Float('Tuition')
    from_date = fields.Datetime('From date')
    to_date = fields.Datetime('To date')
    description = fields.Text('Description')

    contract_tuition = fields.Integer('Contract Tuition')
    actual_tuition = fields.Integer('Tuition')
    material_price = fields.Integer('Material Price')
    total_amount = fields.Integer('Total', compute='_compute_total_amount', store=True)
    note = fields.Char('Note')
    retains = fields.Selection([('rate', 'Rate'), ('fixed', 'Fixed')], required=True, default='rate')
    rate = fields.Float('Rate (%)', default=1)
    fixed_amount = fields.Float('Fixed amount', default=0)
    refund_rate = fields.Float('Refund rate (%)', default=0)
    assistant_support = fields.Float('Assistant Support', default=0)
    teacher_remuneration = fields.Float('Teacher remuneration', default=0)
    outside = fields.Float('Outside', default=0)
    tax = fields.Float('Tax (%)', default=0)
    tuition_cit_tax = fields.Float('CIT tax tuition', default=0)
    p_tuition_cit_tax = fields.Float('CIT tax tuition (%)', default=0)
    material_cit_tax = fields.Float('CIT tax material', default=0)
    material_vat_tax = fields.Float('Vat tax material', default=0)
    p_material_cit_tax = fields.Float('CIT Tax Material (%)', default=0)
    p_material_vat_tax = fields.Float('VAT Tax Material (%)', default=0)
    students_deal = fields.Integer('Students deal', default=0)
    infra_fee = fields.Float('Infra Fee', default=0)
    keep_tuition = fields.Integer('Keep Tuition', default=0)
    keep_material = fields.Integer('Keep Material', default=0)


    topic_ids = fields.One2many('gdsg_contract.core.topic', 'contract_id')

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

    @api.onchange('actual_tuition','material_price')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.actual_tuition + rec.material_price

class Gdsg_Contract_Topic(models.Model):
    _name = 'gdsg_contract.core.topic'
    _description = 'Contract Topic'

    contract_id = fields.Many2one('gdsg_contract.core', string='Contract')
    name = fields.Char('Topic name', required=True)
    time = fields.Integer('Time', required=True)
    description = fields.Char('Description')