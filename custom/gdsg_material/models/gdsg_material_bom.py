from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError

class Material_Bom(models.Model):
    _name = 'gdsg_material.bom'
    _description = 'Material Bom'

    name = fields.Char('BOM', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('refuse', 'Refuse'),
        ('export', 'Export'),
        ('cancel', 'Cancel')
    ], readonly=True, required=True, string='State', default='new')
    contract_id = fields.Many2one('gdsg_contract.core', string='Contract', required=True)
    material_price = fields.Float('Material Price', compute='_compute_material_price')
    topic_id = fields.Many2one('gdsg_contract.core.topic', string='Contract Topic', required=True, domain="[('contract_id','=',contract_id)]")
    time = fields.Integer('Time', compute='_compute_time', store=True)
    min_student = fields.Float('Minimum Student', compute='_compute_min_student', store=True)
    group_student = fields.Integer('Student / Group', required=True)
    class_student = fields.Integer('Student / Class')
    line_ids = fields.One2many('gdsg_material.bom.line', 'bom_id')

    @api.depends('contract_id')
    def _compute_material_price(self):
        self.material_price = self.contract_id.material_price

    @api.depends('topic_id')
    def _compute_time(self):
        self.time = self.topic_id.time

    @api.depends('material_price','time','line_ids.amount')
    def _compute_min_student(self):
        try:
            if self.material_price:
                line_sum = 0
                for line in self.line_ids:
                    line_sum += line.amount
                self.min_student = (line_sum / self.material_price) / 4 * self.time
            else:
                self.min_student = 0
        except Exception as e:
            pass

    @api.model
    def create(self, vals):
        min_student = 0
        if vals.get('material_price'):
            line_sum = 0
            for line in vals.get('line_ids'):
                line_sum += line[2]['amount']
            min_student = (line_sum / vals.get('material_price')) / 4 * vals.get('time')
        if float(vals.get('group_student')) < min_student:
            raise ValidationError(_("Group student can lower than min student"))
        if vals.get('class_student') < 0:
            raise ValidationError(_("Class student must be greater than zero"))
        res = super(Material_Bom, self).create(vals)
        return res

    def write(self, vals):
        if 'class_student' in vals:
            if vals['class_student'] < 0:
                raise ValidationError(_("Class student must be greater than zero"))
        if 'group_student' in vals:
            if float(vals['group_student']) < self.min_student:
                raise ValidationError(_("Group student can lower than min student"))
        return super(Material_Bom, self).write(vals)

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

    def action_export(self):
        self.state = 'export'


class Material_Bom_Line(models.Model):
    _name = 'gdsg_material.bom.line'
    _description = 'Material Bom Line'

    bom_id = fields.Many2one('gdsg_material.bom', string='Lines')
    product_id = fields.Many2one('product.template')
    quantity = fields.Integer('Quantity', required=True)
    uom_id = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom', store=True)
    require = fields.Char('Require')
    amount = fields.Float('Amount', compute='_compute_amount', store=True)
    note = fields.Char('Note')
    use_for = fields.Selection([('student', 'Student'),('group', 'Group'),('class', 'Class')],
                                    required=True, default='student')
    total_export = fields.Float('Total export', compute='_compute_total_export')
    in_stock = fields.Float('In stock', compute='_compute_in_stock')

    @api.depends('product_id')
    def _compute_uom(self):
        for line in self:
            line.uom_id = line.product_id.uom_id

    @api.onchange('product_id')
    def _compute_amount(self):
        for line in self:
            line.update({
                'amount': line.product_id.standard_price,
            })

    @api.depends('product_id')
    def _compute_in_stock(self):
        stock_warehouse = self.env['stock.warehouse'].sudo().search([('code', '=', 'WHNEW')])
        for line in self:
            product_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', line.product_id.id)])
            stock_quant = self.env['stock.quant'].sudo().search(
                [('location_id', '=', stock_warehouse.lot_stock_id.id), ('product_id', '=', product_product.id)],
                limit=1)
            line.in_stock = stock_quant.available_quantity


    @api.depends('product_id','quantity','use_for','bom_id.class_student','bom_id.group_student')
    def _compute_total_export(self):
        for line in self:
            if line.use_for == 'student':
                line.total_export = line.quantity * line.bom_id.class_student
            elif line.use_for == 'group':
                line.total_export = line.quantity * line.bom_id.group_student
            elif line.use_for == 'class':
                line.total_export = line.quantity