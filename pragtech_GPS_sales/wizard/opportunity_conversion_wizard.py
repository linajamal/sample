from odoo import models, fields, api

class OpportunityConversionWizard(models.TransientModel):
    _name = 'opportunity.conversion.wizard'
    _description = 'Opportunity Conversion Wizard'

    def action_opportunity_conversion(self):
        active_order = self.env.context.get('active_id')
        if not active_order:
            return False

        lead = self.env['crm.lead'].browse(active_order)
        if lead.exists():
            conversion_wizard = self.env['crm.lead2opportunity.partner'].create({
                'partner_id': lead.partner_id.id,
                'user_id': lead.user_id.id,
                'team_id': lead.team_id.id,
                'lead_id': lead.id,
            })
            return conversion_wizard.action_apply()
        
        return False

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
