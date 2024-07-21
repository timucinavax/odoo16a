from odoo import models, fields, api, tools, _


class Material_Bom(models.Model):
    _name = 'gdsg_material.bom'
    _description = 'Material Bom'

    name = fields.Char('BOM', required=True)
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract', required=True)
    material_price = fields.Float('Material Price')
    topic_id = fields.Many2one('gdsg_contract.core.topic', string='Contract Topic', required=True, domain="[('contract_id','=',contract_id)]")
    time = fields.Integer('Time', compute='_compute_time')
    min_student = fields.Float('Minimum Student', compute='_compute_min_student')
    group_student = fields.Integer('Student / Group', required=True)
    line_ids = fields.One2many('gdsg_material.bom.line', 'bom_id')

    @api.onchange('topic_id')
    def _compute_time(self):
        self.time = self.topic_id.time

    @api.onchange('material_price','time','line_ids.amount')
    def _compute_min_student(self):
        line_sum = 0
        for line in self.line_ids:
            line_sum += line.amount
        self.min_student = (line_sum / self.material_price) / 4 * self.time

    # @api.model
    # def create(self, vals):
    #     line_sum = 0
    #     for line in vals['line_ids']:
    #         line_sum += line[2]['amount']
    #     topic = self.env['gdsg_contract.core.topic'].sudo().search([('id','=',vals['topic_id'])])
    #     rs = (line_sum / vals['material_price']) / 4 * topic.time
    #     vals['min_student'] = rs
    #     res = super(Material_Bom, self).create(vals)
    #     return res
    #
    # @api.model
    # def write(self, records, value):
    #     line_sum = 0
    #     for line in self.line_ids:
    #         line_sum += line.amount
    #     rs = (line_sum / self.material_price) / 4 * self.time
    #     self.min_student = rs
    #     return super().write(records, value)


class Material_Bom_Line(models.Model):
    _name = 'gdsg_material.bom.line'
    _description = 'Material Bom Line'

    bom_id = fields.Many2one('gdsg_material.bom', string='Lines')
    product_id = fields.Many2one('product.template')
    quantity = fields.Integer('Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom')
    require = fields.Char('Require')
    amount = fields.Float('Amount')
    note = fields.Char('Note')
    use_for = fields.Selection([('student', 'Student'),('group', 'Group'),('class', 'Class')],
                                    required=True, default='student')

    @api.onchange('product_id')
    def _compute_uom(self):
        self.uom_id = self.product_id.uom_id