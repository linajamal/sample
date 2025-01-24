from odoo import models, fields, api
from odoo.exceptions import ValidationError

class VehicleStatusConfirmationWizard(models.TransientModel):
    _name = 'vehicle.status.confirmation.wizard'
    _description = 'Vehicle Status Confirmation Wizard'

    def action_update_vehicle_status(self):
        active_status_id = self.env.context.get('active_id')
        if active_status_id:
            status = self.env['fleet.manage.status'].browse(active_status_id)
            if status:
                for line in status.line_ids:
                    if not line.new_status:
                        raise ValidationError(f"Line no:{line.s_no} does not have a New Status to update.")
                    line.vehicle_id.status = line.new_status
                    line.state = 'submitted'
                status.state = 'submitted'

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
