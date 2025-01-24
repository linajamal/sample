from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [
        ('unique_default_code', 'UNIQUE(default_code)', 'The internal reference must be unique.')
    ]
    
    imei = fields.Char(
        string='IMEI',
        help='Enter the IMEI number of the device'
    )
    brand_id = fields.Many2one(
        'product.brand', 
        string='Brand',
        help='Select the brand of the device'
    )
    operating_system = fields.Many2one('merge.device.os', 'Operating System')
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires."
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Subscription Expiration Plan',
    )
    
    @api.onchange('imei')
    def _onchange_imei(self):
        if self.imei:
            self.barcode = self.imei
        else:
            self.barcode = False
            
    @api.depends('default_code', 'name')
    def _compute_display_name(self):
        for product in self:
            product.display_name = product.default_code

    @api.onchange('default_code')
    def _onchange_default_code(self):
        if not self.default_code:
            return

        domain = [('default_code', '=', self.default_code)]
        if self.id.origin:
            domain.append(('id', '!=', self.id.origin))

        if self.env['product.template'].search_count(domain, limit=1):
            return
            # return {'warning': {
            #     'title': _("Note:"),
            #     'message': _("The Internal Reference '%s' already exists.", self.default_code),
            # }}
