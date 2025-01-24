from odoo import api, models, fields
from odoo.exceptions import ValidationError

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _rec_name = 'maintenance_id'
    
    vehicle_id = fields.Many2one(
        'fleet.vehicle', 
        'Vehicle', 
        required=True
    )
    custom_state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ], string="State", default='draft')
    maintenance_id = fields.Char('Maintenance ID', readonly=True, default='New')
    service_type_id = fields.Many2one(
        'fleet.service.type', 'Service Type', required=False,
        default=lambda self: self.env.ref('fleet.type_service_service_7', raise_if_not_found=False),
    )
    vehicle_plate_word = fields.Char(string="Vehicle Plate Word")
    vehicle_plate_number = fields.Char(string="Vehicle Plate Number")
    vehicle_serial_number = fields.Char(string="Vehicle Serial Number")
    vehicle_invoice_number = fields.Char(string="Vehicle Invoice Number")
    vehicle = fields.Char(string="Vehicle ID")
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned to')
    access_ids = fields.Many2many(
        'res.users',
        'res_users_maintenance_rel',
        'fleet_maintenance_id',
        'user_id',
        string='Access IDs'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    city = fields.Char(string='City')
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    request_status = fields.Selection([
        ('non_technical', 'Non Technical'),
        ('non_technical_invoiced', 'Non Technical - Invoiced'),
        ('technical_invoiced', 'Technical - Invoiced'),
        ('technical_no_device_change', 'Technical - No Device Change'),
        ('technical_device_change', 'Technical - Device Change'),
        ('technical_sim_change', 'Technical - SIM Change'),
    ], string='Request Status', default='non_technical')
    is_create_order = fields.Boolean(string='Is Create Order?',
        #compute='_compute_is_create_order', store=True
        )
    is_invoice_item = fields.Boolean(string='Is Invoice Item?',
        #compute='_compute_is_invoice_item', store=True
        )
    is_device_change = fields.Boolean(string='Is Device Change?',
        #compute='_compute_is_device_change', store=True
        )
    is_sim_change = fields.Boolean(string='Is SIM Change?',
        #compute='_compute_is_sim_change', store=True
        )
    invoice_item = fields.Many2one(
        'product.template',
        string='Invoice Item',
        domain=[('type', '=', 'service'), ('payment_term_id', '=', False)],
    )
    invoice_amount = fields.Monetary(
        string='Invoice Amount',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    order_count = fields.Integer(string='Invoice Count', #compute='_compute_order_count'
        )
    transfer_count = fields.Integer(string='Transfer Count', #compute='_compute_transfer_count'
        )
    related_invoice_ids = fields.Many2many(
        'account.move', 
        string="Related Invoice"
    )
    related_transfer_ids = fields.Many2many(
        'stock.picking', 
        string="Related Transfers"
    )
    device_warranty_expiration_date = fields.Date(
        string="Device Warranty Expiration Date",
        help="The date when the device warranty expires.")
    device_warranty_status = fields.Selection([
        ('bad_usage', 'Bad Usage'),
        ('within_warranty_period', 'Within the Warranty Period'),
        ('without_warranty_period', 'Outside the Warranty Period')
    ], string='Device Warranty Status')
    #old_device_details_ids = fields.One2many('old.device.details', 'old_device_details_id', string="Old Device Details")
    #old_sim_details_ids = fields.One2many('old.sim.details', 'old_sim_details_id', string="Old SIM Details")
    barcode = fields.Many2one(
        'merge.device', 
        string="Barcode", 
        help="Merged Product ID's",
        domain=[('state', '=', 'merged')]
    )
    source_wh = fields.Many2one('stock.location', 'Source Warehouse',
                                domain="[('usage', '=', 'internal')]")
    destination_wh = fields.Many2one('stock.location', 'Target Warehouse',
                                     #domain="[('is_destination', '=', 'True')]"
                                     )
    new_device_code = fields.Many2one('product.template', 'Device Code',
            #domain="[('tracking', '=', 'serial'), ('operating_system', '=', False), ('id', 'in', available_device_ids)]"
            )
    device_lot_ids = fields.Many2many('stock.lot', 'device_lots','vehicle_id','lot_id', string='Device Lots',
            compute='_compute_device_lot_ids', store=False
    )
    new_device_imei = fields.Char('Device IMEI')
    new_device_imei = fields.Many2one('stock.lot', 'Device IMEI',
                                    domain="[('id', 'in', device_lot_ids)]")
    sim_lot_ids = fields.Many2many('stock.lot', string='Lots',
            compute='_compute_sim_lot_ids', store=False
    )
    available_device_ids = fields.Many2many('product.template','products_rel', string='Available Devices',
    #        compute='_compute_available_device_ids', store=False
    )
    available_sim_ids = fields.Many2many(
        'product.template', 
        #compute='_compute_available_sim_ids', 
        string='Available SIM Codes'
    )
    new_sim_code = fields.Many2one('product.template', 'SIM Code',
            #domain="[('id', 'in', available_sim_ids), ('operating_system', '!=', False), ('tracking', '=', 'serial')]"
            )
    new_sim_serial_no = fields.Many2one('stock.lot', 'SIM Serial No.',
                                    domain="[('id', 'in', sim_lot_ids)]")


    @api.onchange('barcode')
    def _onchange_barcode(self):
        """Populates other fields based on the selected barcode."""
        if self.barcode:
            # Assuming `merge.device` model has the related fields to populate these values
            self.source_wh = self.barcode.source_wh.id
            self.destination_wh = self.barcode.destination_wh.id
            self.new_device_code = self.barcode.device_code.id
            self.new_device_imei = self.barcode.device_imei.id
        else:
            # Reset fields if barcode is removed
            self.source_wh = False
            self.destination_wh = False
            self.new_device_code = False
            self.new_device_imei = False

    @api.depends('new_sim_code')
    def _compute_sim_lot_ids(self):
        for record in self: 
            if record.new_sim_code and record.source_wh:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', record.new_sim_code.id),
                    ('location_id', '=', record.source_wh.id),
                    ('quantity', '>', 0)
                ])
                record.sim_lot_ids = quants.mapped('lot_id').ids
            else:
                record.sim_lot_ids = []

    @api.depends('new_device_code')
    def _compute_device_lot_ids(self):
        for record in self: 
            if record.new_device_code and record.source_wh:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', record.new_device_code.id),
                    ('location_id', '=', record.source_wh.id),
                    ('quantity', '>', 0)
                ])
                record.device_lot_ids = quants.mapped('lot_id').ids
            else:
                record.device_lot_ids = []
    '''
    @api.onchange('old_device_details_ids')
    def _onchange_old_device_details_ids(self):
        for index, line in enumerate(self.old_device_details_ids):
            line.s_no = index + 1
    
    @api.onchange('old_sim_details_ids')
    def _onchange_old_sim_details_ids(self):
        for index, line in enumerate(self.old_sim_details_ids):
            line.s_no = index + 1
    
    @api.depends('source_wh')
    def _compute_available_device_ids(self):
        for record in self:
            if record.source_wh:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', record.source_wh.id),
                    ('quantity', '>', 0)
                ])
                record.available_device_ids = quants.mapped('product_id.product_tmpl_id')
            else:
                record.available_device_ids = self.env['product.template']
    
    @api.depends('source_wh')
    def _compute_available_sim_ids(self):
        for record in self:
            if record.source_wh:
                quants = self.env['stock.quant'].search([
                    ('location_id', '=', record.source_wh.id),
                    ('quantity', '>', 0)
                ])
                record.available_sim_ids = quants.mapped('product_id.product_tmpl_id')
            else:
                record.available_sim_ids = self.env['product.template']
    
    
                
    
                     
    def _compute_order_count(self):
        for record in self:
            if record.maintenance_id:
                invoices = self.env['sale.order'].search([
                    ('maintenance_id', '=', record.maintenance_id)
                ])
                record.order_count = len(invoices)
                # if invoices:
                #     record.related_invoice_ids = [(6, 0, invoices.ids)]
            else:
                record.order_count = 0
    
    def _compute_transfer_count(self):
        for record in self:
            if record.maintenance_id:
                transfers = self.env['stock.picking'].search([
                    ('origin', '=', record.maintenance_id)
                ])
                record.transfer_count = len(transfers)
                # if transfers:
                #     record.related_transfer_ids = [(6, 0, transfers.ids)]
            else:
                record.transfer_count = 0
            
    @api.onchange('invoice_item')
    def _onchange_invoice_item(self):
        for record in self:
            record.invoice_amount = record.invoice_item.list_price if record.invoice_item else 0.0
            
    @api.model
    def create(self, vals):
        if vals.get('maintenance_id', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('fleet.maintenance.sequence')
            vals['maintenance_id'] = sequence
        if vals['assigned_to']:
            vals['access_ids'] = [(4, vals['assigned_to'], 0)]
        else:
            vals['access_ids'] = vals.get('access_ids', [])
        vals['access_ids'] += [(4, self.env.user.id, 0)]
        admin_users = self.env['res.users'].search([('groups_id.name', '=', 'GPS Tracking / Admin')])
        admin_user_ids = [admin_user.id for admin_user in admin_users if admin_user.id not in vals.get('access_ids', [])]
        vals['access_ids'] += [(4, admin_id, 0) for admin_id in admin_user_ids]
        return super(FleetVehicleLogServices, self).create(vals)
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            if self.vehicle_id.sales_invoice_number:
                invoice = self.env['account.move'].search([
                    ('name', '=', self.vehicle_id.sales_invoice_number)
                ], limit=1)
                self.device_warranty_expiration_date = invoice.warranty_expiration_date
            else:
                self.device_warranty_expiration_date = False
            if self.vehicle_id.line_ids:
                self.old_device_details_ids = [(5, 0, 0)]
                self.old_sim_details_ids = [(5, 0, 0)]
                self.old_device_details_ids = [
                    (0, 0, {
                        'device_code': line.device_code.id,
                        'device_name': line.device_name,
                        'device_imei': line.device_imei,
                        'qty': 1,
                        'warehouse': line.warehouse.id,
                        'old_device_details_id': self.id
                    }) for line in self.vehicle_id.line_ids
                ]
                self.old_sim_details_ids = [
                    (0, 0, {
                        'sim_code': line.sim_code.id,
                        'sim_serial_no': line.sim_serial_no.id,
                        'qty': 1,
                        'warehouse': line.warehouse.id,
                        'old_sim_details_id': self.id
                    }) for line in self.vehicle_id.line_ids
                ]
            else:
                self.old_device_details_ids = [(5, 0, 0)]
                self.old_sim_details_ids = [(5, 0, 0)]
            self.vehicle_plate_word = self.vehicle_id.vehicle_plate_word
            self.vehicle_serial_number = self.vehicle_id.vehicle_serial_number
            self.customer_id = self.vehicle_id.customer_id.id
            self.vehicle_invoice_number = self.vehicle_id.sales_invoice_number
            self.vehicle = self.vehicle_id.vehicle_id
            self.street = self.vehicle_id.customer_id.street
            self.street2 = self.vehicle_id.customer_id.street2
            self.city = self.vehicle_id.customer_id.city
            self.state_id = self.vehicle_id.customer_id.state_id.id
            self.zip = self.vehicle_id.customer_id.zip
            self.country_id = self.vehicle_id.customer_id.country_id.id
        else:
            self.vehicle_plate_word = False
            self.vehicle_serial_number = False
            self.customer_id = False
            self.vehicle_invoice_number = False
            self.vehicle = False
            self.street = False
            self.street2 = False
            self.city = False
            self.state_id = False
            self.zip = False
            self.country_id = False
            self.device_warranty_expiration_date = False
            self.old_device_details_ids = [(5, 0, 0)]
            self.old_sim_details_ids = [(5, 0, 0)]
    
    @api.depends('request_status', 'device_warranty_status')
    def _compute_is_create_order(self):
        for record in self:
            if record.request_status in ['non_technical_invoiced', 'technical_invoiced']:
                record.is_create_order = True
            elif record.request_status == 'technical_device_change' and record.device_warranty_status in ['bad_usage', 'without_warranty_period']:
                record.is_create_order = True
            else:
                record.is_create_order = False
    
    @api.depends('request_status')
    def _compute_is_invoice_item(self):
        for record in self:
            if record.request_status in ['non_technical_invoiced', 'technical_invoiced']:
                record.is_invoice_item = True
            else:
                record.is_invoice_item = False

    @api.depends('request_status')
    def _compute_is_device_change(self):
        for record in self:
            record.is_device_change = record.request_status in ['technical_device_change']

    @api.depends('request_status')
    def _compute_is_sim_change(self):
        for record in self:
            record.is_sim_change = record.request_status in ['technical_sim_change']
            
    def action_submit(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'transfer.confirmation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pragtech_GPS_maintenance.view_transfer_confirmation_wizard').id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }

    def action_create_so(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.order.confirmation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pragtech_GPS_maintenance.view_maintenance_order_confirmation_wizard').id,
            'target': 'new',
            'context': {
                'active_id': self.id,
            }
        }
                
    def action_maintenance_order(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Order',
                'res_model': 'sale.order',
                'view_mode': 'list',
                'domain': [('maintenance_id', '=', self.maintenance_id)],
                'target': 'current',
            }
    
    def action_maintenance_transfer(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Maintenance Transfer',
                'res_model': 'stock.picking',
                'view_mode': 'list',
                'domain': [('origin', '=', self.maintenance_id)],
                'target': 'current',
            }


    '''