from odoo import api, models, fields

class StockLocationInherit(models.Model):
    _inherit = 'stock.location'
    
    is_destination = fields.Boolean(string="Is Target?")