from odoo import models, fields, api

class InvoiceGenerationWizard(models.TransientModel):
    _name = 'invoice.generation.wizard'
    _description = 'Invoice Generation Wizard'

    def action_invoice_generation(self):
        active_order_id = self.env.context.get('active_id')
        if active_order_id:
            order = self.env['sale.order'].browse(active_order_id)
            
            # Prepare data for the advance payment record
            advance_payment_data = {
                'advance_payment_method': 'delivered',  # or 'percentage', 'fixed' based on your requirement
                'sale_order_ids': [(6, 0, [order.id])],  # Link to your sale order
            }
            
            # Create the advance payment record
            advance_payment = self.env['sale.advance.payment.inv'].create(advance_payment_data)
            # Call the create_invoices method to generate the invoice
            return advance_payment.create_invoices()

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
