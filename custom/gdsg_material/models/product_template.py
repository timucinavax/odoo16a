from odoo import models, fields, api, tools, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_uom_id = fields.Many2one('uom.uom', 'Purchase Uom')