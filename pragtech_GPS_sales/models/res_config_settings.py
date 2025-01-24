from odoo import models, fields

class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    google_maps_api_token = fields.Char(
        string='Google Maps API Token',
        help='Enter your Google Maps API token here.'
    )

    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        google_maps_api_token = self.env['ir.config_parameter'].sudo().get_param('google_maps_api_token')
        res.update(
            google_maps_api_token = google_maps_api_token,
        )
        return res
    
    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('google_maps_api_token', self.google_maps_api_token)
