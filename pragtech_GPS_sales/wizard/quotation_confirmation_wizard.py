from odoo import models, fields, api

class QuotationConfirmationWizard(models.TransientModel):
    _name = 'quotation.confirmation.wizard'
    _description = 'Quotation Confirmation Wizard'

    def action_confirm_quotation(self):
        # here trying to call that base function from my custom wizard
        active_order = self.env.context.get('active_id')
        order = self.env['sale.order'].browse(active_order)
        if order:
            order.partner_id.commercial_id = order.commercial_id
            order.partner_id.customer_group_id = order.customer_group_id.id
            order.partner_id.leads = False
            return order.action_confirm()

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
