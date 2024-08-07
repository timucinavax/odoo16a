from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError
from collections import defaultdict

class Material_Purchase_Request(models.Model):
    _name = 'gdsg_material.purchase.request'
    _description = 'Material Purchase Request'

    name = fields.Char('Name', required=True)
    bom_ids = fields.Many2many('gdsg_material.bom', 'res_gdsg_material_pr_bom_rel', 'pr_id','bom_id', string='BOMs')
    line_ids = fields.One2many('gdsg_material.purchase.request.line', 'pr_id')

    def action_generate_data(self):
        self.line_ids.unlink()
        line_list = []
        for bom in self.bom_ids:
            for bom_line in bom.line_ids:
                line_list.append(dict(product_id=bom_line.product_id.id,
                                      total_export=bom_line.total_export))
        grouped_data = defaultdict(float)
        for item in line_list:
            grouped_data[item['product_id']] += item['total_export']
        result = [{'product_id': k, 'total_export': v} for k, v in grouped_data.items()]
        for line in result:
            # product_template = self.env['product.template'].sudo().browse(line['product_id'])
            self.line_ids.create(dict(pr_id=self.id
                                        , product_id=line['product_id']
                                        , total_export=line['total_export']))
        self.env.cr.commit()
        print(result)
        # self.line_ids.create(dict(product=))


class Material_Purchase_Request_Line(models.Model):
    _name = 'gdsg_material.purchase.request.line'
    _description = 'Material Purchase Request Line'

    pr_id = fields.Many2one('gdsg_material.purchase.request', string='Lines')
    product_id = fields.Many2one('product.template', domain="[('detailed_type','=','product')]")
    total_export = fields.Float('Total Export')
    uom_id = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom', store=True)
    in_stock = fields.Float('In stock', compute='_compute_in_stock')
    request_purchase = fields.Float('Request Purchase', compute='_compute_uom')
    convert_uom_id = fields.Many2one('uom.uom', string='Uom', compute='_compute_uom', store=True)
    convert_request_purchase = fields.Float('Convert Request Purchase')

    @api.depends('product_id')
    def _compute_uom(self):
        for line in self:
            line.uom_id = line.product_id.uom_id.id
            line.convert_uom_id = line.product_id.purchase_uom_id.id
            line.request_purchase = line.total_export - line.in_stock
            line.convert_request_purchase = (line.total_export - line.in_stock) * line.product_id.uom_id.factor / line.product_id.purchase_uom_id.factor

    @api.depends('product_id')
    def _compute_in_stock(self):
        stock_warehouse = self.env['stock.warehouse'].sudo().search([('code', '=', 'WHNEW')])
        for line in self:
            product_product = self.env['product.product'].sudo().search([('product_tmpl_id', '=', line.product_id.id)])
            stock_quant = self.env['stock.quant'].sudo().search(
                [('location_id', '=', stock_warehouse.lot_stock_id.id), ('product_id', '=', product_product.id)],
                limit=1)
            line.in_stock = stock_quant.available_quantity

