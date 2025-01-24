from odoo import api, models, fields
from odoo.exceptions import ValidationError
import re

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    #_name = 'fleet.vehicle'
    #_inherit = ['fleet.vehicle','portal.mixin', 'product.catalog.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting For Approval'),
        ('submitted', 'Submitted'),
    ], string="Document Status", default='draft')
    status = fields.Selection([
        ('active', 'Active'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled')
    ], string='Vehicle Status', default='active')
    vehicle_id = fields.Char('Vehicle ID', readonly=True, default='New')
    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned to')
    task_id = fields.Char('Task ID')
    sales_invoice_number = fields.Char('Sales Invoice No.')
    last_subscription_plan = fields.Many2one(
        'product.template',
        string='Last Subscription',
        domain=[('type', '=', 'service')],
    )
    subscription_expiration_date = fields.Date(
        string="Subscription Expiration Date",
        help="The date when the subscription expires.")
    # new_subscription_expiration_date = fields.Date(
    #     string="New Subscription Expiration Date",
    #     help="The date when the subscription expires.")
    # is_subscription_date_matched = fields.Boolean(
    #     string="Is Subscription Date Matched",
    #     compute="_compute_is_subscription_date_matched",
    #     store=True
    # )
    plate_image = fields.Selection([
        ('url', 'URL'),
        ('attachment', 'Attachment')
    ], string="Plate Image", default='url')
    plate_image_url = fields.Char(string="Plate Image URL")
    plate_image_attachment = fields.Many2many(
        'ir.attachment',
        'plate_image_attachment_rel',
        'fleet_id',
        'attach_id',
        string='Add',
    )
    custom_state_id = fields.Many2one(
        'res.country.state', 
        string="State", 
        help="State where the vehicle is registered.",
        domain="[('country_id', '=', custom_country_id)]"
    )
    custom_country_id = fields.Many2one(
        'res.country', 
        string="Country", 
        help="Country where the vehicle is registered."
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
    )
    customer_signature = fields.Binary(
        string='Customer Signature',
    )
    installation_date_time = fields.Datetime(string='Installation Time')
    barcode = fields.Many2one(
        'merge.device', 
        string="Barcode", 
        help="Merged Product ID's",
        domain=[('state', '=', 'merged')]
    )
    vehicle_plate_word = fields.Char(string="Vehicle Plate Word")
    vehicle_serial_number = fields.Char(string="Vehicle Serial Number")
    #line_ids = fields.One2many('fleet.vehicle.line', 'fleet_id', string="Items")
    access_ids = fields.Many2many(
        'res.users',
        'res_users_access_rel',
        'fleet_vehicle_id',
        'user_id',
        string='Access IDs'
    )

    gps_tracking_enabled = fields.Boolean(string="GPS Tracking Enabled")

   