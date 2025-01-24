from odoo import models, fields, api

class TrainingPopupWizard(models.TransientModel):
    _name = 'training.popup.wizard'
    _description = 'Training Popup Wizard'

    is_training_required = fields.Boolean(string="Is Training Required?")
    reason = fields.Text(string="Reason", help="Provide a reason if training is not required.")

    @api.onchange('is_training_required')
    def _onchange_is_training_required(self):
        """Clear the reason when training is required."""
        if self.is_training_required:
            self.reason = False

    def action_confirm(self):
        """Confirm action to update the parent model."""
        active_id = self.env.context.get('active_id')
        if active_id:
            record = self.env['project.task'].browse(active_id)
            record.custom_state = 'submitted'
            record.installation_date_time = fields.Datetime.now()
            record.is_training_required = self.is_training_required
            record.reason = self.reason
            record.vehicles_to_confirm_ids.filtered(lambda vehicle: vehicle).action_submit()
        return {'type': 'ir.actions.act_window_close'}
