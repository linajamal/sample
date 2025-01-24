from odoo import models, fields, api
from odoo.exceptions import UserError

class MergeDevice(models.Model):
    _name = 'merge.device'
    _description = 'Merge Device'
    _order = 'id desc'
    _rec_name = 'barcode'
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('merged', 'Merged'),
        ], string="State")
    merge_device_id = fields.Char('Merge Device ID', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('merge.device.sequence'))
    barcode = fields.Char('Barcode')
    source_wh = fields.Many2one('stock.location', 'Source Warehouse', required=True,
                                domain="[('usage', '=', 'internal')]")
    destination_wh = fields.Many2one('stock.location', 'Target Warehouse', required=True,
                                     domain="[('is_destination', '=', 'True')]")
    device_code = fields.Many2one('product.template', 'Device Code', required=True,
            domain="[('tracking', '=', 'serial'), ('operating_system', '=', False), ('id', 'in', available_device_ids)]")
    
    # device_imei = fields.Char('Device IMEI')
    device_imei = fields.Many2one('stock.lot', 'Device IMEI',
                                    domain="[('id', 'in', device_lot_ids)]")
    device_name = fields.Char('Device Name')
    
    description = fields.Html(string="Description")
    