from odoo import models, fields

class CustomerGroup(models.Model):
    _name = 'customer.group'
    _description = 'Customer Group'

    name = fields.Char(string='Group Name', required=True)
