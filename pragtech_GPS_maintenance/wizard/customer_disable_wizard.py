from odoo import models, fields, api

class CustomerDisableWizard(models.TransientModel):
    _name = 'customer.disable.wizard'
    _description = 'Customer disable Wizard'

    def action_disable_customer(self):
        active_status_id = self.env.context.get('active_id')
        if active_status_id:
            status = self.env['fleet.manage.status'].browse(active_status_id)
            if status:
                status.customer.write({'active': False})
                status.state = 'submitted'

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
