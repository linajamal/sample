# -*- encoding: utf-8 -*-
{
    'name': 'Pragtech GPS Maintenance',
    'version': '18.0',
    'category': 'Fleet',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://pragtech.co.in',
    'depends': ['pragtech_GPS_technical', 'fleet', 'account_fleet'],
    'summary': 'This module manages the full lifecycle of vehicle maintenance, status control, and subscription renewals, streamlining requests, invoicing, and updates for customer vehicles.',
    'description': """Pragtech GPS Maintenance Module""",
    "data": [
        'data/fleet_maintenance_sequence.xml',
        #'data/fleet_manage_status_sequence.xml',
        #'data/sale_subscription_sequence.xml',
        #'data/general_subscription_product.xml',
        #'security/ir.model.access.csv',
        'views/fleet_maintenance_inherit_view.xml',
        #'views/fleet_manage_status_view.xml',
        #'views/sale_subscription_view.xml',
        #'wizard/transfer_confirmation_wizard.xml',
        #'wizard/customer_enable_wizard.xml',
        #'wizard/customer_disable_wizard.xml',
        #'wizard/vehicle_status_confirmation_wizard.xml',
        #'wizard/vehicle_subscription_confirmation_wizard.xml',
        #'wizard/maintenance_order_confirmation_wizard.xml'
    ],
    'assets': {
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
