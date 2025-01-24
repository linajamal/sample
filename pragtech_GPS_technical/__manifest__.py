# -*- encoding: utf-8 -*-
{
    'name': 'Pragtech GPS Technical',
    'version': '18.0',
    'category': 'Task',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://pragtech.co.in',
    'depends': ['account', 'project', 'stock', 'purchase', 'sale_project', 'sale', 'sale_management', 'pos_sale', 'fleet'],
    'summary': 'This module manages the full lifecycle of installation tasks, device management, and maintenance for customer vehicles, streamlining setup, tracking, and upkeep processes.',
    'description': """Pragtech GPS Technical Module""",
    "data": [
        #'security/ir.model.access.csv',
        #'data/project_task_sequence.xml',
        #'data/merge_device_sequence.xml',
        #'data/fleet_vehicle_sequence.xml',
        #'views/account_move_inherit_view.xml',
        #views/sale_order_inherit_view.xml',
        #'report/account_move_report_view.xml',
        #'views/project_task_inherit_view.xml',
        'views/fleet_vehicle_inherit_view.xml',
        #'views/merge_device_view.xml',
        #'views/product_brand_view.xml',
        #'views/product_template_inherit_view.xml',
        #'views/merge_device_os_view.xml',
        #'views/stock_location_inherit_view.xml',
        #'wizard/training_popup_wizard.xml'
    ],
    'assets': {
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
