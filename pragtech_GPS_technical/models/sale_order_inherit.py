from odoo import models, api, fields,  _ 
from odoo.exceptions import ValidationError, UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    custom_compute = fields.Many2one(
        comodel_name='account.payment.term',
        string='Subscription Expiration Due Compute',
        compute="_compute_payment_terms",
        store=True)
    
    @api.depends('order_line.product_template_id')
    def _compute_payment_terms(self):
        for record in self:
            # print('---------------check')
            if record.sales_type != 'subscription':
                service_lines = record.order_line.filtered(
                lambda line: line.product_template_id.type == 'service'
                )
                if service_lines:
                    record.custom_compute = service_lines.product_template_id.payment_term_id.id if service_lines else False
                    record.payment_term_id = record.custom_compute.id

                else:
                    record.custom_compute = False
            else:
                record.custom_compute = False
