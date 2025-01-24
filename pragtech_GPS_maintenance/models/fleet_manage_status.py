from odoo import api, models, fields
from odoo.exceptions import UserError

class FleetManageStatus(models.Model):
    _name = 'fleet.manage.status'
    _description = 'Customer and Vehicle Status Management'
    _rec_name = 'status_id'
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('waiting_for_approval', 'Waiting For Approval'),
            ('submitted', 'Submitted'),
        ], string="State", default='draft')
    status_id = fields.Char('Status ID', default=lambda self: self.env['ir.sequence'].next_by_code('fleet.manage.status.sequence'))
    date = fields.Date(string="Date", required=True)
    customer = fields.Many2one(
        'res.partner',
        string="Customer",
        domain=['&', '|', ('active', '=', True), ('active', '=', False), ('customer_rank', '>', 0)],
    )
    type = fields.Selection(
        [
            ('customer', 'Customer'),
            ('vehicle', 'Vehicle')
        ],
        string="Type",
        required=True
    )
    new_customer_state = fields.Selection(
        [
            ('enable', 'Enable'),
            ('disable', 'Disable')
        ],
        string="New Customer State",
    )
    remarks = fields.Html(string="Remarks")
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    vehicle_plate_word = fields.Char(string="Vehicle Plate Word")
    vehicle_serial_number = fields.Char(string="Vehicle Serial Number")
    is_customer = fields.Boolean(string="Is Customer", compute="_compute_flags", store=True)
    is_vehicle = fields.Boolean(string="Is Vehicle", compute="_compute_flags", store=True)
    line_ids = fields.One2many('fleet.manage.status.line', 'fleet_status_id', string="Customer Vehicles")
    
    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        for index, line in enumerate(self.line_ids):
            line.s_no = index + 1
            
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.vehicle_plate_word = self.vehicle_id.vehicle_plate_word
            self.vehicle_serial_number = self.vehicle_id.vehicle_serial_number
        else:
            self.vehicle_plate_word = False
            self.vehicle_serial_number = False
            
    @api.depends('type')
    def _compute_flags(self):
        for record in self:
            record.is_customer = record.type == 'customer'
            record.is_vehicle = record.type == 'vehicle'
            
    @api.model
    def create(self, vals):
        if not vals.get('status_id'):
            vals['status_id'] = self.env['ir.sequence'].next_by_code('fleet.manage.status.sequence')
        return super(FleetManageStatus, self).create(vals)
    
    def action_send_for_approval(self):
        self.state = 'waiting_for_approval'
        
    def action_submit(self):
        if self.type == 'customer' and self.new_customer_state == 'enable':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'customer.enable.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_maintenance.view_customer_enable_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
        if self.type == 'customer' and self.new_customer_state == 'disable':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'customer.disable.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_maintenance.view_customer_disable_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
        if self.type == 'vehicle':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'vehicle.status.confirmation.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_maintenance.view_vehicle_status_confirmation_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
    
    def action_add(self):
        if self.vehicle_id:
            self.line_ids = [(0, 0, {
                'vehicle_id': self.vehicle_id.id,
                'customer_id': self.vehicle_id.customer_id.id,
                'old_status': self.vehicle_id.status,
                'subscription_expiration_date': self.vehicle_id.subscription_expiration_date,
            })]
            self._onchange_line_ids()
            
    def action_refresh(self):
        self.vehicle_id = False
        self.vehicle_plate_word = False
        self.vehicle_serial_number = False

class FleetManageStatusLine(models.Model):
    _name = 'fleet.manage.status.line'
    _description = 'Fleet Manage Status Line for Vehicles'

    fleet_status_id = fields.Many2one('fleet.manage.status', string="Fleet Status", ondelete='cascade', readonly=True)
    s_no = fields.Integer(string="S.No.", readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', readonly=True)
    customer_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    old_status = fields.Selection([
        ('active', 'Active'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled')
    ], string='Old Status', readonly=True)
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires.", readonly=True)
    new_status = fields.Selection([
        ('active', 'Active'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled')
    ], string='New Status')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], string='State', default='draft', readonly=True)

    @api.model
    def unlink(self):
        if self.state == 'submitted':
            raise UserError('You cannot delete lines when the state is "Submitted".')
        return super(FleetManageStatusLine, self).unlink()