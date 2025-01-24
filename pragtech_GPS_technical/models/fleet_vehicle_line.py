from odoo import models, fields

class FleetVehicleLine(models.Model):
    _name = 'fleet.vehicle.line'
    _description = 'Fleet Line for Products'

    fleet_id = fields.Many2one('fleet.vehicle', string="Fleet", ondelete='cascade', readonly=True)
    s_no = fields.Integer(string="S.No.", readonly=True)
    device_code = fields.Many2one('product.template', 'Device Code', readonly=True)
    device_name = fields.Char(string="Device Name", readonly=True)
    device_imei = fields.Char(string="Device IMEI", readonly=True)
    sim_code = fields.Many2one('product.template', 'Sim Code', readonly=True)
    sim_serial_no = fields.Many2one('stock.lot', 'SIM Serial No.', readonly=True)
    qty = fields.Float(string="Quantity", readonly=True)
    warehouse = fields.Many2one('stock.location', 'Warehouse', readonly=True)