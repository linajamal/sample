from odoo import models, api, fields,  _ 
from odoo.exceptions import ValidationError, UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    vat_registration_type = fields.Selection([
        ('url', 'URL'),
        ('attachment', 'Attachment')
    ], string="VAT Registration Type", default='url')

    commercial_id_type = fields.Selection([
        ('url', 'URL'),
        ('attachment', 'Attachment')
    ], string="Commercial ID Type", default='url')

    transfer_receipt_type = fields.Selection([
        ('url', 'URL'),
        ('attachment', 'Attachment')
    ], string="Transfer Receipt Type", default='url')
    
    other_type = fields.Selection([
        ('url', 'URL'),
        ('attachment', 'Attachment')
    ], string="Other", default='url')

    # URL fields
    vat_registration_url = fields.Char(string="VAT Registration URL")
    commercial_id_url = fields.Char(string="Commercial ID URL")
    transfer_receipt_url = fields.Char(string="Transfer Receipt URL")
    other_url = fields.Char(string="Other URL")

    # Attachment fields (Binary)
    # vat_registration_attachment = fields.Binary(string="VAT Registration Attachment")
    # commercial_id_attachment = fields.Binary(string="Commercial ID Attachment")
    # transfer_receipt_attachment = fields.Binary(string="Transfer Receipt Attachment")
    
    vat_registration_attachment = fields.Many2many(
        'ir.attachment',
        'vat_attachment_rel',
        'pro_id',
        'attach_id',
        string='Add',
    )

    commercial_id_attachment = fields.Many2many(
        'ir.attachment',
        'commercial_id_attachment_rel',
        'pro_id',
        'attach_id',
        string='Add',
    )

    transfer_receipt_attachment = fields.Many2many(
        'ir.attachment',
        'transfer_receipt_attachment_rel',
        'pro_id',
        'attach_id',
        string='Add',
    )
    
    other_attachment = fields.Many2many(
        'ir.attachment',
        'other_attachment_rel',
        'pro_id',
        'attach_id',
        string='Add',
    )

    commercial_id = fields.Char(string='Commercial ID')
    customer_group_id = fields.Many2one(
        'customer.group',
        string='Customer Group'
    )
    is_submitted = fields.Boolean(string="Is Submitted?")
    GNRLSUB = fields.Boolean(string="Is GNRLSUB?")
    source = fields.Char(string='Source')
    # custom_compute = fields.Many2one(
    #     comodel_name='account.payment.term',
    #     string='Subscription Expiration Due Compute',
    #     compute="_compute_payment_terms",
    #     store=True)
    sales_type = fields.Selection([
        ('sales', 'Sales'),
        ('maintenance', 'Maintenance'),
        ('subscription', 'Subscription'),
    ], string='Sales Type', default='sales')
    maintenance_id = fields.Char(string='Maintenance ID')
    vehicle_ids = fields.Many2many(
        'fleet.vehicle',
        'fleet_vehicle_sale_rel',
        'task_sequence_id',
        'vehicle_id',
        string='Vehicle IDs'
    )
    vehicle_expiration_date = fields.Date(
        string="Vehicle Max Expiration Date",
        help="The date when the vehicle expires.",
    )
    last_subscription_plan = fields.Many2one(
        'product.template',
        string='Last Subscription',
        domain=[('type', '=', 'service')],
    )
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires."
    )
    
    @api.onchange('partner_id')
    def _onchange_partner_related(self):
        for record in self:
            if record.partner_id:
                record.commercial_id = record.partner_id.commercial_id
                record.customer_group_id = record.partner_id.customer_group_id.id
            else:
                record.commercial_id = False
                record.customer_group_id = False

            
    @api.constrains('commercial_id')
    def _check_commercial_id_length(self):
        for record in self:
            if record.commercial_id:
                commercial_id_digits = ''.join(filter(str.isdigit, record.commercial_id))
                if len(commercial_id_digits) != 10:
                    raise ValidationError("The Commercial ID must be exactly 10 digits.")
    
    # @api.depends('order_line.product_template_id')
    # def _compute_payment_terms(self):
    #     for record in self:
    #         if record.sales_type != 'subscription':
    #             service_lines = record.order_line.filtered(
    #             lambda line: line.product_template_id.type == 'service'
    #             )
    #             if service_lines:
    #                 record.custom_compute = service_lines.product_template_id.payment_term_id.id if service_lines else False
    #                 record.payment_term_id = record.custom_compute.id

    #             else:
    #                 record.custom_compute = False
    #         else:
    #             record.custom_compute = False

                 
    def action_confirm_trigger(self):
        
        # for rec in self:
        #     if rec.sales_type == 'sales':
        #         for line in rec.order_line:
        #             if not line.serial_numbers:
        #                 raise UserError(
        #                     f"The serial number is missing for the product '{line.product_id.display_name}' in the sale order line."
        #                 )
    
        # for order in self:
            # if order.partner_id.leads or not order.partner_id.commercial_id or not order.partner_id.customer_group_id:
            #     raise UserError(_("Please create a customer with commercial id and customer group before confirming the quotation."))
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'quotation.confirmation.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_sales.view_quotation_confirmation_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }

    def action_create_customer(self):
        for order in self:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': order.partner_id.id,
                'target': 'current',
            }
    
    def submit_so(self):
        for order in self:
            if not order.vat_registration_url and not order.vat_registration_attachment:
                raise UserError(_("Please provide either a VAT Registration URL or Attachment."))
            
            if not order.commercial_id_url and not order.commercial_id_attachment:
                raise UserError(_("Please provide either a Commercial ID URL or Attachment."))
            
            if not order.transfer_receipt_url and not order.transfer_receipt_attachment:
                raise UserError(_("Please provide either a Transfer Receipt URL or Attachment."))
            
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.order.submit.wizard',
                    'view_mode': 'form',
                    'view_id': self.env.ref('pragtech_GPS_sales.view_sale_order_submit_wizard').id,
                    'target': 'new',
                    'context': {
                        'active_id': self.id,
                    }
                }
            
    def create_invoices_trigger(self):
        for order in self:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'invoice.generation.wizard',
                    'view_mode': 'form',
                    'view_id': self.env.ref('pragtech_GPS_sales.view_invoice_generation_wizard').id,
                    'target': 'new',
                    'context': {
                        'active_id': self.id,
                    }
                }


# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'

#     serial_numbers = fields.Many2one('stock.lot',
#         string="Serial Numbers",
#         domain="[('product_id', '=', product_id)]"
#     )


# class StockMoveLine(models.Model):
#     _inherit = 'stock.move.line'


#     quant_id = fields.Many2one(
#         'stock.quant', 
#         string="Pick From", 
#         compute='_compute_quant_id', 
#         store=True
#     )

#     @api.depends('move_id.sale_line_id.serial_numbers', 'product_id', 'location_id')
#     def _compute_quant_id(self):
#         for line in self:
#             if line.move_id.sale_line_id:
#                 serial_number = line.move_id.sale_line_id.serial_numbers
#                 print("___________________serial_number________",serial_number)

#                 # Find the related stock.quant record
#                 stock_quant = self.env['stock.quant'].search([
#                     ('lot_id', '=', serial_number.id),
#                     ('product_id', '=', line.product_id.id),
#                     ('location_id', '=', line.location_id.id)
#                 ], limit=1)
#                 print("___________________stock_quant________",stock_quant)
#                 if stock_quant:
#                     line.quant_id = stock_quant.id
#                 else:
#                     line.quant_id = False

# class StockPickingInherit(models.Model):
#     _inherit = "stock.picking"


#     def fetch_sim(self):
#         print("button ready aaayi")


  



class SaleAdvancePaymentInvInherit(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    
    def create_invoices(self):
        self._check_amount_is_positive()
        invoices = self._create_invoices(self.sale_order_ids)
        if self.sale_order_ids.sales_type == 'sales':
            invoices.write({
                    'invoice_type': 'sales'
                })
        elif self.sale_order_ids.sales_type == 'maintenance':
            invoices.write({
                    'invoice_type': 'maintenance',
                    'maintenance_id': self.sale_order_ids.maintenance_id
                })
        elif self.sale_order_ids.sales_type == 'subscription':
            invoices.write({
                    'invoice_type': 'subscription',
                    'vehicle_expiration_date': self.sale_order_ids.vehicle_expiration_date,
                    'last_subscription_plan': self.sale_order_ids.last_subscription_plan.id,
                    'vehicle_ids': [(6, 0, self.sale_order_ids.vehicle_ids.ids)]
                })
        return self.sale_order_ids.action_view_invoice(invoices=invoices)
