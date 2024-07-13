from odoo import models, fields, api, tools, _
import re
import logging

_logger = logging.getLogger('gdsg_refund_core')

class Refund_Core(models.Model):
    _name = 'gdsg_refund.core'
    _description = 'Refund Core'

    name = fields.Char('Title', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract', required=True, domain="[('partner_id', '=', partner_id)]")
    transaction_id = fields.Many2one('gdsg_contract.transaction', string='Revenue', required=True, domain="[('contract_id', '=', contract_id)]")
    refund_period = fields.Char('Refund period', required=True)
    structure_id = fields.Many2one('gdsg_refund.structure', string='Structure', required=True)
    description = fields.Char('Description')
    lesson = fields.Integer('Lesson')
    refund_school = fields.Integer('School percent')
    refund_company = fields.Integer('Company percent')
    material_price = fields.Integer('Material price')
    tuition_price = fields.Integer('Tuition price')
    refund_line = fields.One2many('gdsg_refund.core.lines', 'refund_core_id')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('gdsg_refund.core') or _('New')
        res = super(Refund_Core, self).create(vals)
        return res

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



