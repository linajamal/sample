from odoo import api, models, fields, _, Command
from datetime import timedelta

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    warranty_expiration_date = fields.Date(
        string="Warranty Expiration Date",
        help="The date when the warranty expires.",
        compute="_compute_warranty_expiration_date",
        store=True
    )
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires.",
        compute="_compute_subscription_expiration_date",
        store=True
    )
    vehicle_expiration_date = fields.Date(
        string="Vehicle Max Expiration Date",
        help="The date when the vehicle expires.",
    )
    last_subscription_plan = fields.Many2one(
        'product.template',
        string='Last Subscription',
        domain=[('type', '=', 'service')],
    )
    custom_compute = fields.Many2one(
        comodel_name='account.payment.term',
        string='Subscription Expiration Due Compute',
        compute="_compute_subscription",
        store=True)
    task_count = fields.Integer(string='Task Count', compute='_compute_task_count')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_maintenance_count')
    related_maintenance_ids = fields.Many2many(
        'fleet.vehicle.log.services', 
        string="Related Maintenances"
    )
    related_project_ids = fields.Many2many(
        'project.task', 
        string="Related Projects"
    )
    invoice_type = fields.Selection([
        ('sales', 'Sales'),
        ('maintenance', 'Maintenance'),
        ('subscription', 'Subscription'),
    ], string='Invoice Type', default='sales')
    maintenance_id = fields.Char(string='Maintenance ID')
    vehicle_ids = fields.Many2many(
        'fleet.vehicle',
        'fleet_vehicle_invoice_rel',
        'task_sequence_id',
        'vehicle_id',
        string='Vehicle IDs'
    )
    GNRLSUB = fields.Boolean(string="Is GNRLSUB?")
    
    def _compute_maintenance_count(self):
        for record in self:
            if record.maintenance_id:
                maintenances = self.env['fleet.vehicle.log.services'].search([
                    ('maintenance_id', '=', record.maintenance_id)
                ])
                record.maintenance_count = len(maintenances)
                # if maintenances:
                #     record.related_maintenance_ids = [(6, 0, maintenances.ids)]
            else:
                record.maintenance_count = 0
                
    def _compute_task_count(self):
        for record in self:
            if record.name:
                projects = self.env['project.task'].search([
                    ('sales_invoice_no', '=', record.name)
                ])
                record.task_count = len(projects)
                # if projects:
                #     record.related_project_ids = [(6, 0, projects.ids)]
            else:
                record.task_count = 0
            
    @api.depends('invoice_line_ids.product_id')
    def _compute_subscription(self):
        for record in self:
            if record.invoice_type != 'subscription':
                service_lines = record.invoice_line_ids.filtered(
                lambda line: line.product_id.type == 'service'
                )
                if service_lines:
                    record.custom_compute = service_lines.product_id.payment_term_id.id if service_lines else False
                    # record.invoice_payment_term_id = record.custom_compute.id

                else:
                    record.custom_compute = False
            else:
                record.custom_compute = False
                
    @api.depends('invoice_date')
    def _compute_subscription_expiration_date(self):
        for record in self:
            if record.invoice_type == 'sales':
                if record.custom_compute and record.invoice_date:
                    days = record.custom_compute.line_ids and record.custom_compute.line_ids[0].nb_days or 0
                    record.subscription_expiration_date = record.invoice_date + timedelta(days=days)
                else:
                    record.subscription_expiration_date = False
            elif record.invoice_type == 'maintenance' and record.invoice_date:
                if record.invoice_payment_term_id and record.invoice_date:
                    days = record.invoice_payment_term_id.line_ids and record.invoice_payment_term_id.line_ids[0].nb_days or 0
                    record.subscription_expiration_date = record.invoice_date + timedelta(days=days)
                else:
                    record.subscription_expiration_date = False
            elif record.invoice_type == 'subscription':
                # print('-----------record.vehicle_ids', record.vehicle_ids)
                if record.vehicle_expiration_date and record.invoice_date:
                    days = record.invoice_payment_term_id.line_ids and record.invoice_payment_term_id.line_ids[0].nb_days or 0
                    if record.GNRLSUB:
                        record.subscription_expiration_date = record.vehicle_expiration_date
                        for vehicle in record.vehicle_ids:
                            vehicle.write({
                                'subscription_expiration_date': record.vehicle_expiration_date,
                                'last_subscription_plan': record.last_subscription_plan.id,
                            })
                    else:
                        record.subscription_expiration_date = record.vehicle_expiration_date + timedelta(days=days)
                        for vehicle in record.vehicle_ids:
                            vehicle.write({
                                'subscription_expiration_date': record.vehicle_expiration_date + timedelta(days=days),
                                'last_subscription_plan': record.last_subscription_plan.id,
                            })
                else:
                    record.subscription_expiration_date = False
                    for vehicle in record.vehicle_ids:
                        vehicle.write({
                            'subscription_expiration_date': vehicle.subscription_expiration_date,
                            'last_subscription_plan': vehicle.last_subscription_plan,
                        })


                
    @api.depends('invoice_date')
    def _compute_warranty_expiration_date(self):
        for record in self:
            if record.invoice_date:
                record.warranty_expiration_date = record.invoice_date + timedelta(days=2 * 365)
            else:
                record.warranty_expiration_date = False
    
    def action_project_task(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Project Task',
                'res_model': 'project.task',
                'view_mode': 'list',
                'domain': [('sales_invoice_no', '=', self.name)],
                'target': 'current',
                'context': {'group_by': 'sales_invoice_no'},
            }
    
    def action_maintenance_record(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Fleet Maintenance',
                'res_model': 'fleet.vehicle.log.services',
                'view_mode': 'list',
                'domain': [('maintenance_id', '=', self.maintenance_id)],
                'target': 'current',
            }
              
    def action_create_installation_task(self):
        for move in self:
            task_lines = []
            total_qty = 0
            
            for invoice_line in move.invoice_line_ids:
                if invoice_line.product_id.type == 'service':
                    continue
            
                task_line_vals = {
                    'product_id': invoice_line.product_id.id,
                    'item_code': invoice_line.product_id.default_code,
                    'qty': invoice_line.quantity,
                }
                task_lines.append((0, 0, task_line_vals)) 
                total_qty += invoice_line.quantity

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_name': 'Installation Task',
                    'default_customer_id': self.partner_id.id,
                    'default_sales_invoice_no': self.name,
                    'default_line_ids': task_lines,
                    # 'default_total_quantity': total_qty,
                    # 'default_remaining': total_qty,
                },
            }

