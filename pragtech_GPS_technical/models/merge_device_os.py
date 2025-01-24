from odoo import models, fields

class MergeDeviceOS(models.Model):
    _name = 'merge.device.os'
    _description = 'Operating System Information'

    name = fields.Char(string='Operating System', required=True)
