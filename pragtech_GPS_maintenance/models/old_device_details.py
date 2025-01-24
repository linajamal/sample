from odoo import models, fields

class OldDeviceDetails(models.Model):
    _name = 'old.device.details'
    _description = 'Old Device Details'

    old_device_details_id = fields.Many2one('fleet.vehicle.log.services', string="Old Device Details", ondelete='cascade', readonly=True)
    s_no = fields.Integer(string="S.No.", readonly=True)
    device_code = fields.Many2one('product.template', 'Device Code', readonly=True)
    device_name = fields.Char(string="Device Name", readonly=True)
    device_imei = fields.Char(string="Device IMEI", readonly=True)
    qty = fields.Float(string="Quantity", readonly=True)
    warehouse = fields.Many2one('stock.location', 'Warehouse', readonly=True)
