from odoo import models, fields, api

class QuotationCreationWizard(models.TransientModel):
    _name = 'quotation.creation.wizard'
    _description = 'Quotation Creation Wizard'

    def action_create_quotation(self):
        # here trying to call that base function from my custom wizard
        active_lead = self.env.context.get('active_id')
        lead = self.env['crm.lead'].browse(active_lead)
        if lead:
            return lead.action_sale_quotations_new()

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
