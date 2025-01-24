from odoo import api, models, fields
from odoo.exceptions import ValidationError, UserError
import json

def get_google_maps_url(latitude, longitude):
    res = "https://maps.google.com?q=%s,%s" % (latitude, longitude)
    return res
    
class CrmLeadInherit(models.Model):
    _inherit = 'crm.lead'
    # _rec_name = 'lead_sequence'

    is_organization = fields.Boolean(string="Is Organization?")
    lead_type = fields.Selection([
        ('new_visit', 'New Visit'),
        ('visit_follow_up', 'Visit Follow Up'),
        ('new_call', 'New Call'),
        ('follow_up_call', 'Follow up on a Call')
    ], string="Lead Type")
    lead_status = fields.Selection([
        ('successful', 'Successful'),
        ('unsuccessful', 'Unsuccessful'),
        ('needs_follow_up', 'Needs Follow Up')
    ], string="Lead Status")
    lead_sequence = fields.Char(string="Lead ID", readonly=True, copy=False)
    probability_selection = fields.Selection([
        ('0', '0'),
        ('50', '50'),
        ('60', '60'),
        ('70', '70'),
        ('80', '80'),
        ('90', '90'),
        ('100', '100'),
    ], string="Probability (Selection)", default='0')
    probability = fields.Float(string="Probability", default=0.0)
    probability_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string="Probability Level", default='low', readonly=True)
    custom_parent_id = fields.Many2one(
        'res.partner',
        string='Custom Parent ID'
    )
    custom_child_id = fields.Many2one(
        'res.partner',
        string='Custom Child ID'
    )
    
    def action_update_address(self):
        self.ensure_one()
        self.sudo().write({
            'street': self.user_id.street,
            'city': self.user_id.city,
            'state_id': self.user_id.state_id.id,
            'zip': self.user_id.zip,
            'country_id': self.user_id.country_id.id
        })
        if self.custom_parent_id:
            self.custom_parent_id.write({
            'street': self.user_id.street,
            'city': self.user_id.city,
            'state_id': self.user_id.state_id.id,
            'zip': self.user_id.zip,
            'country_id': self.user_id.country_id.id
        })
        if self.custom_child_id:
            self.custom_child_id.write({
            'street': self.user_id.street,
            'city': self.user_id.city,
            'state_id': self.user_id.state_id.id,
            'zip': self.user_id.zip,
            'country_id': self.user_id.country_id.id
        })
        
    def action_open_map_view(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': get_google_maps_url(self.user_id.partner_id.latitude, self.user_id.partner_id.longitude),
            'target': 'new'
        }
        
    @api.onchange('probability_selection')
    def _onchange_probability_selection(self):
        if self.probability_selection:
            self.probability = float(self.probability_selection)

    @api.onchange('probability')
    def _onchange_probability(self):
        if self.probability == 0:
            self.probability_level = 'low'
        if self.probability <= 50:
            self.probability_level = 'low'
        elif self.probability <= 70:
            self.probability_level = 'medium'
        elif self.probability <= 90:
            self.probability_level = 'high'
        else:
            self.probability_level = 'high'
            
    @api.model
    def create(self, vals):
        # Set the lead sequence if not already set
        if 'lead_sequence' not in vals or not vals['lead_sequence']:
            vals['lead_sequence'] = self.env['ir.sequence'].next_by_code('crm.lead.sequence') or '/'

        # Case when no partner is set (i.e., partner_id is not provided)
        if not vals.get('partner_id'):
            partner_vals = self._prepare_partner_vals(vals)

            if vals.get('is_organization'):
                # Case 2: is_organization = True and contact_name is provided
                partner = self.env['res.partner'].create(partner_vals)

                if vals.get('contact_name'):
                    contact_vals = self._prepare_contact_vals(vals, partner)
                    contact = self.env['res.partner'].create(contact_vals)
                    partner.write({'child_ids': [(4, contact.id)]})
                    vals['custom_child_id'] = contact.id

                vals['partner_id'] = partner.id
                vals['custom_parent_id'] = partner.id

            else:
                # Case 1: is_organization = False
                partner_vals['name'] = vals.get('contact_name')  # Use contact_name as partner name
                partner = self.env['res.partner'].create(partner_vals)
                vals['partner_id'] = partner.id
                vals['custom_child_id'] = partner.id
        return super(CrmLeadInherit, self).create(vals)


    # def write(self, vals):
    #     for record in self:
    #         if not record.partner_id:
    #             partner_vals = self._prepare_partner_vals(vals)
    #             if vals.get('is_organization'):
    #                 partner = self.env['res.partner'].create(partner_vals)

    #                 if vals.get('contact_name'):
    #                     contact_vals = self._prepare_contact_vals(vals, partner)
    #                     contact = self.env['res.partner'].create(contact_vals)
    #                     partner.write({'child_ids': [(4, contact.id)]})

    #                 vals['partner_id'] = partner.id

    #             else:
    #                 partner_vals['name'] = vals.get('contact_name')  # Use contact_name as partner name
    #                 partner = self.env['res.partner'].create(partner_vals)
    #                 vals['partner_id'] = partner.id
    #         else:
    #             partner_vals = self._prepare_partner_vals(vals)
    #             record.partner_id.write(partner_vals)
    #             if vals.get('is_organization'):
    #                 if vals.get('contact_name'):
    #                     contact_vals = self._prepare_contact_vals(vals, record.partner_id)
    #                     contact = self.env['res.partner'].search([
    #                         ('parent_id', '=', record.partner_id.id),
    #                         ('name', '=', vals.get('contact_name'))
    #                     ], limit=1)
    #                     test = self.env['res.partner'].search([
    #                         ('id', '=', 43),
    #                     ], limit=1)
    #                     if contact:
    #                         contact.write(contact_vals)
    #                     else:
    #                         new_contact = self.env['res.partner'].create(contact_vals)
    #                         record.partner_id.write({'child_ids': [(4, new_contact.id)]})
    #                 else:
    #                     contact_vals = self._prepare_contact_vals(vals, record.partner_id)
    #                     self.env['res.partner'].create(contact_vals)

    #             if vals.get('partner_name'):
    #                 record.partner_id.write({'name': vals['partner_name']})

    #     return super(CrmLeadInherit, self).write(vals)


    def _prepare_contact_vals(self, vals, parent_partner):
        """Prepare contact values based on the lead data, link it to the parent partner."""
        contact_vals = {
            'name': vals.get('contact_name') or self.contact_name,
            'street': vals.get('street') or self.street,
            'street2': vals.get('street2') or self.street2,
            'city': vals.get('city') or self.city,
            'state_id': vals.get('state_id') or self.state_id.id,
            'zip': vals.get('zip') or self.zip,
            'country_id': vals.get('country_id') or self.country_id.id,
            'title': vals.get('title') or self.title,
            'email': vals.get('email_from') or self.email_from,
            'phone': vals.get('phone') or self.phone,
            'mobile': vals.get('mobile') or self.mobile,
            'is_company': False,
            'leads': True,
            'parent_id': parent_partner.id,
        }
        return contact_vals

    def _prepare_partner_vals(self, vals):
        """Prepare partner values from lead data."""
        partner_name = vals.get('contact_name') if not vals.get('is_organization') else vals.get('partner_name')
        partner_vals = {
            'name': partner_name or self.partner_name or self.contact_name,
            'street': vals.get('street') or self.street,
            'street2': vals.get('street2') or self.street2,
            'city': vals.get('city') or self.city,
            'state_id': vals.get('state_id') or self.state_id.id,
            'zip': vals.get('zip') or self.zip,
            'country_id': vals.get('country_id') or self.country_id.id,
            'title': vals.get('title') or self.title,
            'source': vals.get('lead_sequence') or self.lead_sequence,
            'email': vals.get('email_from') or self.email_from,
            'phone': vals.get('phone') or self.phone,
            'mobile': vals.get('mobile') or self.mobile,
            'is_company': vals.get('is_organization', False) or self.is_organization,
            'leads': True,
        }
        return partner_vals


    @api.constrains('mobile', 'country_id')
    def _check_mobile_number_length(self):
        for record in self:
            if record.mobile:
                # Remove whitespace and check for the '+' symbol
                mobile = record.mobile.strip()
                mobile = mobile[1:]
                # if not mobile.startswith('+'):
                #     raise ValidationError("The mobile number must start with the '+' symbol.")

                # Remove the '+' and extract digits only
                phone_digits = ''.join(filter(str.isdigit, mobile))

                country = record.country_id or self.env.user.country_id
                if country:
                    country_code = str(country.phone_code or '')
                    if phone_digits.startswith(country_code):
                        phone_digits = phone_digits[len(country_code):]

                # Validate length (10 to 14 digits allowed)
                if not (1 <= len(phone_digits) <= 14):
                    raise ValidationError("The mobile number must be between 1 and 14 digits.")
    
    # @api.constrains('mobile', 'country_id')
    # def _check_mobile_number_length(self):
    #     for record in self:
    #         if record.mobile:
    #             phone_digits = ''.join(filter(str.isdigit, record.mobile))

    #             country = record.country_id or self.env.user.country_id
    #             if country:
    #                 country_code = str(country.phone_code or '')
    #                 if phone_digits.startswith(country_code):
    #                     phone_digits = phone_digits[len(country_code):]

    #             if len(phone_digits) != 10:
    #                 raise ValidationError("The mobile number must be exactly 10 digits.")
    
    def action_convert_opportunity_trigger(self):
        for lead in self:
            return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'opportunity.conversion.wizard',
                    'view_mode': 'form',
                    'view_id': self.env.ref('pragtech_GPS_sales.view_opportunity_conversion_wizard').id,
                    'target': 'new',
                    'context': {
                        'active_id': self.id,
                    }
                }

        
    def convert_opportunity(self, partner, user_ids=False, team_id=False):
        customer = partner if partner else self.env['res.partner']
        email_from = partner.email
        phone = partner.phone
        for lead in self:
            if not lead.active or lead.probability == 100:
                continue
            vals = lead._convert_opportunity_data(customer, team_id)
            lead.write(vals)

        if user_ids or team_id:
            self._handle_salesmen_assignment(user_ids=user_ids, team_id=team_id)

        return True
    
    def action_sale_quotations_new_custom(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'quotation.creation.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_sales.view_quotation_creation_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
    
    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = self._prepare_opportunity_quotation_context()
        action['context']['search_default_opportunity_id'] = self.id
        action['context']['default_source'] = self.lead_sequence
        action['context']['default_commercial_id'] = self.partner_id.commercial_id if self.partner_id.commercial_id else False
        action['context']['default_customer_group_id'] = self.partner_id.customer_group_id.id if self.partner_id.customer_group_id else False
        return action
        
class Lead2OpportunityPartnerInherit(models.TransientModel):
    _name = 'crm.lead2opportunity.partner'
    _inherit = 'crm.lead2opportunity.partner'
    _description = 'Convert Lead to Opportunity (not in mass)'

    @api.model
    def default_get(self, fields):
        """ Allow support of active_id / active_model instead of just default_lead_id
        to ease window action definitions, and be backward compatible. """
        result = super(Lead2OpportunityPartnerInherit, self).default_get(fields)

        if 'lead_id' in fields and not result.get('lead_id') and self.env.context.get('active_id'):
            result['lead_id'] = self.env.context.get('active_id')

        if result.get('lead_id'):
            if self.env['crm.lead'].browse(result['lead_id']).probability == 100:
                raise UserError(_("Closed/Dead leads cannot be converted into opportunities."))

        if 'action' in fields and not result.get('action'):
            result['action'] = 'nothing'

        return result

