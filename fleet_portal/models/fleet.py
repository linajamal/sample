from odoo import api, fields, models, _, Command, SUPERUSER_ID, modules, tools
import logging 
from odoo import fields
import urllib

import binascii

from odoo.fields import Command

_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = 'fleet.vehicle'


    def get_portal_url(self, suffix=None):
        """
            Get a portal url for this model, including access_token.
            The associated route must handle the flags for them to have any effect.
            - suffix: string to append to the url, before the query string
            - report_type: report_type query string, often one of: html, pdf, text
            - download: set the download query string to true
            - query_string: additional query string
            - anchor: string to append after the anchor #
        """
        self.ensure_one()
        _logger.info('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMm')
        #url='/request/accept'
        url = '/request/'+str(self.id) + suffix if suffix else ''
        _logger.info(url)
        return url