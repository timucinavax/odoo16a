from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = "res.company"

    store_keeper = fields.Char('Store Keeper')
    chief_accountant = fields.Char('Chief Accountant')
    president = fields.Char('President')