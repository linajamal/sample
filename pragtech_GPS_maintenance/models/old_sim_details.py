from odoo import models, fields

class OldSimDetails(models.Model):
    _name = 'old.sim.details'
    _description = 'Old SIM Details'

    old_sim_details_id = fields.Many2one('fleet.vehicle.log.services', string="Old SIM Details", ondelete='cascade', readonly=True)
    s_no = fields.Integer(string="S.No.", readonly=True)
    sim_code = fields.Many2one('product.template', 'Sim Code', readonly=True)
    sim_serial_no = fields.Many2one('stock.lot', 'SIM Serial No.', readonly=True)
    qty = fields.Float(string="Quantity", readonly=True)
    warehouse = fields.Many2one('stock.location', 'Warehouse', readonly=True)
