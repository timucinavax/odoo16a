from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_printexcel(self):
        try:
            data = {
                'form_data': self.read()[0]
            }
            return self.env.ref('gdsg_material.report_gdsg_stock_picking_xlsx').report_action(self, data=data)
        except Exception as e:
            raise ValidationError(_(e))