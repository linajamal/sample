from odoo.addons.project.controllers.portal import ProjectCustomerPortal
import base64

from odoo import http
from odoo.http import request


class ProjectCustomerPortal(ProjectCustomerPortal):

    def _create_and_upload_attach(self, res_id, file, filename):
        return request.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file.read()),
            'res_model': 'project.task',
            'res_id': res_id
        })

    @http.route('/upload/task/attachment', type='http', auth='public', website=True)
    def upload_attachment(self, **kw):
        task_id = int(kw['task'])
        if kw.get('add_attachment', False):
            file = kw['add_attachment']
            self._create_and_upload_attach(task_id, file, file.filename)
        return request.redirect(f'/my/task/{task_id}')
