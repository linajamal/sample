from odoo import api, models, fields

class ProjectTaskInherit(models.Model):
    _inherit = 'project.task'
    
    task_sequence = fields.Char(string="Task ID", readonly=True, copy=False)
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer'
    )
    sales_invoice_no = fields.Char(string='Sales Invoice No.')
    total_quantity = fields.Integer(string='Total Quantity',
                                    compute='_compute_total_quantity')
    remaining = fields.Integer(string='Remaining',
                               compute='_compute_remaining')
    ready_to_confirm = fields.Integer(string='Ready to Confirm',
                               compute='_compute_ready_to_confirm')
    done = fields.Integer(string='Done',
                          compute='_compute_done')
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned to')
    installation_date_time = fields.Datetime(string='Installation Time')
    vehicle_created = fields.Integer(string='Vehicle Created',
        compute='_compute_vehicle_created')
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], default='draft', string="Status")
    is_task_created = fields.Boolean(
        string="Task Created",
        compute="_compute_is_task_created")
    is_task_completed = fields.Boolean(
        string="Task Completed",
        compute="_compute_is_task_completed")
    is_training_required = fields.Boolean(
        string="Training Required")
    reason = fields.Html(
        string="Reason")
    vehicle_count = fields.Integer(string='Vehicle Count', compute='_compute_vehicle_count')
    vehicles_to_confirm_ids = fields.Many2many(
        'fleet.vehicle',
        'fleet_vehicle_task_rel',
        'task_sequence_id',
        'vehicle_id',
        string='Vehicles to Confirm',
        compute='_compute_ready_to_confirm',
        store=True
    )
    related_vehicle_ids = fields.Many2many(
        'fleet.vehicle', 
        string="Related Vehicles"
    )
    line_ids = fields.One2many('project.task.line', 'task_id', string="Items")        
    notes =  fields.Char('Note')  
    def action_fleet_vehicle(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Fleet Vehicle',
                'res_model': 'fleet.vehicle',
                'view_mode': 'list',
                'domain': [('task_id', '=', self.task_sequence)],
                'target': 'current',
            }
        
    def _compute_vehicle_count(self):
        for record in self:
            if record.task_sequence:
                vehicles = self.env['fleet.vehicle'].search([
                    ('task_id', '=', record.task_sequence)
                ])
                record.vehicle_count = len(vehicles)
                # if vehicles:
                #     record.related_vehicle_ids = [(6, 0, vehicles.ids)]
            else:
                record.vehicle_count = 0
            
    def _compute_is_task_created(self):
        for record in self:
            if record.total_quantity == record.vehicle_created or record.total_quantity == record.done:
                record.is_task_created = True
            else:
                record.is_task_created = False
    
    def _compute_is_task_completed(self):
        for record in self:
            if record.custom_state == 'submitted':
                record.is_task_completed = False
            elif record.total_quantity == record.ready_to_confirm:
                record.is_task_completed = True
            else:
                record.is_task_completed = False
                       
    def _compute_vehicle_created(self):
        for record in self:
            record.vehicle_created = self.env['fleet.vehicle'].search_count([
                ('task_id', '=', record.task_sequence)
            ])
    
    def _compute_total_quantity(self):
        for record in self:
            total_qty = 0
            for line in record.line_ids:
                total_qty += line.qty
            record.total_quantity = total_qty
        
    def _compute_remaining(self):
        for record in self:
            record.remaining = record.total_quantity - record.done
    
    def _compute_ready_to_confirm(self):
        for record in self:
            vehicles = self.env['fleet.vehicle'].search([
                ('task_id', '=', record.task_sequence), ('state', '=', 'waiting_for_approval')
            ])
            
            record.ready_to_confirm = len(vehicles)
            vehicle_tuples = [(6, 0, [vehicle.id for vehicle in vehicles])]
            record.vehicles_to_confirm_ids = vehicle_tuples
    
    def _compute_done(self):
        for record in self:
            record.done = self.env['fleet.vehicle'].search_count([
                ('task_id', '=', record.task_sequence), ('state', '=', 'submitted')
            ])
            
    def action_create_customer_vehicle(self):
        invoice = self.env['account.move'].search([('name', '=', self.sales_invoice_no)], limit=1)
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'fleet.vehicle',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_name': 'Fleet Vehicle',
                    'default_assigned_to': self.assigned_to.id,
                    'default_task_id': self.task_sequence,
                    'default_sales_invoice_number': self.sales_invoice_no,
                    'default_subscription_expiration_date': invoice.subscription_expiration_date,
                    # 'default_custom_state_id': invoice.partner_id.state_id.id,
                    # 'default_custom_country_id': invoice.partner_id.country_id.id,
                    'default_customer_id': invoice.partner_id.id,
                    
                },
            }
        
    def action_submit(self):
        return {
        'name': 'Training Confirmation',
        'type': 'ir.actions.act_window',
        'res_model': 'training.popup.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'active_id': self.id},
    }

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        for index, line in enumerate(self.line_ids):
            line.s_no = index + 1
            
    @api.model
    def create(self, vals):
        if 'task_sequence' not in vals or not vals['task_sequence']:
            task_id = self.env['ir.sequence'].next_by_code('project.task.sequence') or '/'
            vals['task_sequence'] = task_id
            vals['name'] = "Installation Task" + ' - ' + str(task_id)
        if vals.get('assigned_to'):
            vals['user_ids'] = [(4, vals['assigned_to'], 0)]
            admin_users = self.env['res.users'].search([('groups_id.name', '=', 'GPS Tracking / Admin')])
            admin_user_ids = [admin_user.id for admin_user in admin_users]
            vals['user_ids'] += [(4, admin_id, 0) for admin_id in admin_user_ids]
        return super(ProjectTaskInherit, self).create(vals)