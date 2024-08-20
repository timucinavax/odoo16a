from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError

class StockLocation(models.Model):
    _inherit = "stock.location"

    report_name = fields.Char('Report Name')
    location_name = fields.Char('Location Name')