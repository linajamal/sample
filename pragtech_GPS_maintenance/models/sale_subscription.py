from odoo import api, models, fields
from odoo.exceptions import ValidationError, UserError

class SaleSubscription(models.Model):
    _name = 'sale.subscription'
    _description = 'Sale Subscription'
    _rec_name = 'subscription_id'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
        ], string="State", default='draft')
    subscription_id = fields.Char('Subscription ID', default=lambda self: self.env['ir.sequence'].next_by_code('sale.subscription.sequence'))
    date = fields.Date(string="Date", required=True)
    customer_id = fields.Many2one(
        'res.partner',
        string="Customer",
    )
    line_ids = fields.One2many('sale.subscription.line', 'sale_subscription_id', string="Subscription Details")
    orders_count = fields.Integer(string='Orders Count', compute='_compute_orders_count')
    is_single_so = fields.Boolean(string="Single SO",
        compute="_compute_is_single_so", store=True)
    vehicle_expiration_date = fields.Date(
        string="Vehicle Max Expiration Date",
        help="The date when the vehicle expires.",
    )
    max_subscription_plan = fields.Many2one(
        'product.template',
        string='Max Subscription',
        domain=[('type', '=', 'service')],
    )
    
    @api.depends('max_subscription_plan')
    def _compute_is_single_so(self):
        for record in self:
            record.is_single_so = bool(record.max_subscription_plan)

    def action_fetch_max_date(self):
        for record in self:
            payment_terms = record.line_ids.filtered(lambda line: line.is_create_so).mapped('new_subscription_plan.payment_term_id')
            # expiration_dates = record.line_ids.filtered(lambda line: line.is_create_so).mapped('subscription_expiration_date')
            expiration_dates = record.line_ids.mapped('subscription_expiration_date')
            filtered_dates = [date for date in expiration_dates if date]
            max_expiration_date = max(filtered_dates) if filtered_dates else None
            if payment_terms:
                max_payment_term = max(payment_terms, key=lambda term: term.line_ids[0].nb_days, default=None)
                line_with_max_term = next(line for line in record.line_ids if line.new_subscription_plan.payment_term_id == max_payment_term)
                record.max_subscription_plan = line_with_max_term.new_subscription_plan.id
                max_expiration_date = max_expiration_date
                record.vehicle_expiration_date = max_expiration_date
            else:
                record.max_subscription_plan = False
                record.vehicle_expiration_date = False
    
    def action_refresh(self):
        self.max_subscription_plan = False
        self.vehicle_expiration_date = False
        
    def _compute_orders_count(self):
        for record in self:
            if record.subscription_id:
                orders = self.env['sale.order'].search([
                    ('source', '=', record.subscription_id)
                ])
                record.orders_count = len(orders)
            else:
                record.orders_count = 0
    
    def action_subscription_orders(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Subscription Orders',
                'res_model': 'sale.order',
                'view_mode': 'list',
                'domain': [('source', '=', self.subscription_id)],
                'target': 'current',
            }
                 
    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        for index, line in enumerate(self.line_ids):
            line.s_no = index + 1
            
    def action_submit(self):
        return {
                'type': 'ir.actions.act_window',
                'res_model': 'vehicle.subscription.confirmation.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('pragtech_GPS_maintenance.view_vehicle_subscription_confirmation_wizard').id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
        
    def action_generate_details(self):
        if self.customer_id:
            vehicles = self.env['fleet.vehicle'].search([('customer_id', '=', self.customer_id.id), ('status', '=', 'active')])
            line_data = []
            for vehicle in vehicles:
                line_data.append((0, 0, {
                    'vehicle_id': vehicle.id,
                    'vehicle_plate_word': vehicle.vehicle_plate_word,
                    'vehicle_serial_number': vehicle.vehicle_serial_number,
                    'subscription_expiration_date': vehicle.subscription_expiration_date,
                    'new_subscription_plan': vehicle.last_subscription_plan.id
                }))
            self.line_ids = line_data
            self._onchange_line_ids()

class SaleSubscriptionLine(models.Model):
    _name = 'sale.subscription.line'
    _description = 'Sale Subscription Line for Renewals'

    sale_subscription_id = fields.Many2one('sale.subscription', string="Sale Subscription", ondelete='cascade', readonly=True)
    is_create_so = fields.Boolean(string="SO")
    s_no = fields.Integer(string="S.No.", readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', readonly=True)
    vehicle_plate_word = fields.Char(string="Vehicle Plate Word", readonly=True)
    vehicle_serial_number = fields.Char(string="Vehicle Serial Number", readonly=True)
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires.", readonly=True)
    # new_subscription_plan = fields.Many2one(
    #     comodel_name='account.payment.term',
    #     string='New Subscription',
    # )
    new_subscription_plan = fields.Many2one(
        'product.template',
        string='New Subscription',
        domain=[('type', '=', 'service')],
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], string='State', default='draft', readonly=True)

    @api.model
    def unlink(self):
        for record in self:
            if record.state == 'submitted':
                raise UserError('You cannot delete lines when the state is "Submitted".')
        return super(SaleSubscriptionLine, self).unlink()
