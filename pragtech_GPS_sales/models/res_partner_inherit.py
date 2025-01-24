from odoo import api, models, fields, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    leads = fields.Boolean(string='Leads', default=False)
    source = fields.Char(string='Source')
    commercial_id = fields.Char(string='Commercial ID')
    customer_group_id = fields.Many2one(
        'customer.group',
        string='Customer Group'
    )
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')
    vehicle_count = fields.Integer(string='Vehicle Count', compute='_compute_vehicle_count')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    subscription_count = fields.Integer(string='Subscription Count', compute='_compute_subscription_count')
    task_count = fields.Integer(string='Task Count', compute='_compute_task_count')
    
    def _compute_vehicle_count(self):
        for record in self:
            if record:
                vehicles = self.env['fleet.vehicle'].search([
                    ('customer_id', '=', record.id)
                ])
                record.vehicle_count = len(vehicles)
            else:
                record.vehicle_count = 0
    
    def _compute_maintenance_count(self):
        for record in self:
            if record:
                maintenances = self.env['fleet.vehicle.log.services'].search([
                    ('customer_id', '=', record.id)
                ])
                record.maintenance_count = len(maintenances)
            else:
                record.maintenance_count = 0
    
    def _compute_subscription_count(self):
        for record in self:
            if record:
                subscriptions = self.env['sale.subscription'].search([
                    ('customer_id', '=', record.id)
                ])
                record.subscription_count = len(subscriptions)
            else:
                record.subscription_count = 0
    
    def _compute_task_count(self):
        for record in self:
            if record:
                tasks = self.env['project.task'].search([
                    ('customer_id', '=', record.id)
                ])
                record.task_count = len(tasks)
            else:
                record.task_count = 0
                
    def action_vehicle_count(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Vehicle Count',
                'res_model': 'fleet.vehicle',
                'view_mode': 'list',
                'domain': [('customer_id', '=', self.id)],
                'target': 'current',
            }
        
    def action_maintenance_count(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Count',
                'res_model': 'fleet.vehicle.log.services',
                'view_mode': 'list',
                'domain': [('customer_id', '=', self.id)],
                'target': 'current',
            }
        
    def action_subscription_count(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Subscription Count',
                'res_model': 'sale.subscription',
                'view_mode': 'list',
                'domain': [('customer_id', '=', self.id)],
                'target': 'current',
            }
        
    def action_task_count(self):
        self.ensure_one()
        action = {
            **self.env["ir.actions.actions"]._for_xml_id("project.project_task_action_from_partner")
        }
        action['domain'] = [('customer_id', '=', self.id)]
        return action
        # return {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Task Count',
        #         'res_model': 'project.task',
        #         'view_mode': 'list',
        #         'domain': [('customer_id', '=', self.id)],
        #         'context': {
        #             'group_by': 'customer_id',
        #         },
        #         'target': 'current',
        #     }
            
    # @api.onchange('commercial_id', 'customer_group_id')
    # def _onchange_commercial_id_and_group(self):
    #     """Set 'leads' to False if both 'commercial_id' and 'customer_group_id' have values."""
    #     if self.commercial_id and self.customer_group_id:
    #         self.leads = False

    @api.constrains('commercial_id', 'customer_group_id')
    def _check_commercial_and_group(self):
        """Ensure 'leads' is False if both 'commercial_id' and 'customer_group_id' have values."""
        for partner in self:
            if partner.commercial_id and partner.customer_group_id:
                partner.leads = False