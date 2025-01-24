from odoo import models, fields, api

class SaleOrderSubmitWizard(models.TransientModel):
    _name = 'sale.order.submit.wizard'
    _description = 'Sale Order Submit Wizard'

    def action_submit_sale_order(self):
        active_order_id = self.env.context.get('active_id')
        if active_order_id:
            order = self.env['sale.order'].browse(active_order_id)
            # order.state = 'submit'
            order.is_submitted = True

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
