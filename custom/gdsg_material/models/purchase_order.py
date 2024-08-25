from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def _compute_partner_ref(self):
        for record in self:
            # Compute logic here
            record.partner_ref = record.partner_id.ref