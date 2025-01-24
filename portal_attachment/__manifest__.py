# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Portal Attachment',
    'version': '18.0.0.1',
    'summary': 'simple module for devs trying to attach from web portal',
    'sequence': 11,
    'description': """
Membership plan
====================
Allow portal user to attach related attachments for tasks 
    """,
    'category': 'Services/Project',
    'author': 'NHS',
    'website': 'https://www.syrupsbiz.com',
    'depends': ['project'],
    'data': [
        'views/project_task_templates.xml',
    ],
    'demo': [
        # 'demo/account_demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_frontend': [
            'portal_attachment/static/src/js/project_task.js',
        ],
    },
    'images':  ['static/description/image_1.jpg', 'static/description/image_2.jpg'],
    'installable': True,
    'application': True,
    'license': 'LGPL-3'
}
