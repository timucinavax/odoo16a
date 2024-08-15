from odoo import models, fields, api, tools, _
import re
import logging

_logger = logging.getLogger('gdsg_refund_core')

class Refund_Core(models.Model):
    _name = 'gdsg_refund.core'
    _description = 'Refund Core'

    name = fields.Char('Title', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('refuse', 'Refuse'),
        ('export', 'Export'),
        ('cancel', 'Cancel')
    ], readonly=True, required=True, string='State', default='new')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract', required=True, domain="[('partner_id', '=', partner_id)]")
    transaction_id = fields.Many2one('gdsg_contract.transaction', string='Revenue', required=True, domain="[('contract_id', '=', contract_id)]")
    refund_period = fields.Char('Refund period', required=True)
    structure_id = fields.Many2one('gdsg_refund.structure', string='Structure', required=True)
    description = fields.Char('Description')
    ratio = fields.Float('Ratio', default=1, inverse='_inverse_ratio')
    refund_school = fields.Integer('School percent')
    refund_company = fields.Integer('Company percent')
    tuition_price = fields.Integer('Tuition price')
    invoice = fields.Char('Invoice', compute='_compute_invoice', store=True)
    invoice_amount = fields.Float('Invoice amount', compute='_compute_invoice', store=True)
    fixed_amount = fields.Float('Fix amount', compute='_compute_contract', store=True)
    actual_tuition = fields.Integer('Actual Tuition', compute='_compute_contract', store=True)
    material_price = fields.Integer('Material Price', compute='_compute_contract', store=True)
    infra_fee = fields.Float('Infra Fee', compute='_compute_contract', store=True)
    outside = fields.Float('Outside', compute='_compute_contract', store=True)
    tuition_cit_tax = fields.Float('CIT Tax Tuition', compute='_compute_contract', store=True)
    p_tuition_cit_tax = fields.Float('CIT Tax Tuition (%)', compute='_compute_contract', store=True)
    material_cit_tax = fields.Float('CIT Tax Material', compute='_compute_contract', store=True)
    material_vat_tax = fields.Float('VAT Tax Material', compute='_compute_contract', store=True)
    p_material_cit_tax = fields.Float('CIT Tax Material (%)', compute='_compute_contract', store=True)
    p_material_vat_tax = fields.Float('VAT Tax Material (%)', compute='_compute_contract', store=True)
    keep_tuition = fields.Integer('Keep Tuition', compute='_compute_contract', store=True)
    keep_material = fields.Integer('Keep Material', compute='_compute_contract', store=True)

    refund_line = fields.One2many('gdsg_refund.core.lines', 'refund_core_id')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gdsg_refund.core') or _('New')
        res = super(Refund_Core, self).create(vals)
        return res

    def action_send_approve(self):
        self.state = 'pending'

    def action_approve(self):
        self.state = 'approved'

    def action_refuse(self):
        self.state = 'refuse'

    def action_cancel(self):
        self.state = 'cancel'

    def action_backtonew(self):
        self.state = 'new'

    @api.onchange('transaction_id')
    def _compute_invoice(self):
        self.invoice = self.transaction_id.invoice_no + self.transaction_id.invoice_code
        self.invoice_amount = self.transaction_id.amount

    @api.onchange('ratio')
    def _inverse_ratio(self):
        self.actual_tuition = self.ratio * self.contract_id.actual_tuition
        self.material_price = self.ratio * self.contract_id.material_price
        self.keep_tuition = self.ratio * self.contract_id.keep_tuition
        self.keep_material = self.ratio * self.contract_id.keep_material

    @api.onchange('contract_id')
    def _compute_contract(self):
        for record in self:
            if record.contract_id:
                record.fixed_amount = record.contract_id.fixed_amount
                record.actual_tuition = record.contract_id.actual_tuition
                record.material_price = record.contract_id.material_price
                record.infra_fee = record.contract_id.infra_fee
                record.outside = record.contract_id.outside
                record.tuition_cit_tax = record.contract_id.tuition_cit_tax
                record.p_tuition_cit_tax = record.contract_id.p_tuition_cit_tax
                record.material_cit_tax = record.contract_id.material_cit_tax
                record.material_vat_tax = record.contract_id.material_vat_tax
                record.p_material_cit_tax = record.contract_id.p_material_cit_tax
                record.p_material_vat_tax = record.contract_id.p_material_vat_tax
                record.keep_tuition = record.contract_id.keep_tuition
                record.keep_material = record.contract_id.keep_material

    def generate_data(self):
        try:
            _logger.info('generate_data start!')
            self.refund_line.unlink()
            refund_line = self.env['gdsg_refund.core.lines'].sudo()
            for structure in self.structure_id:
                sorted_rules = sorted(structure.rule_ids, key=lambda rule: rule.sequence)
                for rule in sorted_rules:
                    python_code = rule.python_code
                    if 'categories' in python_code:
                        pattern = r'categories\.(\w+)'
                        categories_matches = re.findall(pattern, python_code)
                        for category in categories_matches:
                            category_id = self.env['gdsg_refund.rule.category'].search([('code','=',category)]).id
                            refund_lines = self.env['gdsg_refund.core.lines'].sudo().search([('refund_core_id','=',self.id),('category_id','=',category_id)])
                            total = 0
                            for refund_line in refund_lines:
                                total += refund_line.amount
                            python_code = python_code.replace('categories.' + category, str(total))
                    else:
                        python_code = python_code.replace('[gdsg_contract.core]', 'self.contract_id')
                    result = eval(python_code)
                    refund_line.create(dict(refund_core_id=self.id,
                                            rule_id=rule.id,
                                            category_id=rule.category_id.id,
                                            amount=result))
                    self.env.cr.commit()
        except Exception as e:
            _logger.error('generate_data exception: %s' % e)

    def export_data_excel(self):
        try:
            _logger.info('export_data_excel start!')
            data = {
                'form_data': self.read()[0]
            }
            return self.env.ref('gdsg_refund.report_gdsg_refund_core_xlsx').report_action(self, data=data)
        except Exception as e:
            _logger.error('export_data_excel exception: %s' % e)
        finally:
            _logger.info('export_data_excel finish!')

class Refund_Core_Line(models.Model):
    _name = 'gdsg_refund.core.lines'
    _description = 'Refund Core Lines'

    refund_core_id = fields.Many2one('gdsg_refund.core', string='Refund Line', required=True)
    rule_id = fields.Many2one('gdsg_refund.rule', string='Rule')
    category_id = fields.Many2one('gdsg_refund.rule.category', string='Category')
    amount = fields.Float('Amount')
    note = fields.Char('Note')
    category_code = fields.Char('Category Code', related='category_id.code', store=True)



