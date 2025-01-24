# -*- encoding: utf-8 -*-
{
    'name': 'Pragtech GPS Sales',
    'version': '18.0',
    'category': 'Sales',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://pragtech.co.in',
    'depends': ['crm', 'base', 'sale_crm', 'sale', 'contacts', 'web', 'website', 'sale_management', 'account', 'accountant'],
    'summary': 'This module streamlines the sales cycle from lead to invoice, providing a clear, organized workflow for managing leads, opportunities, and customers.',
    'description': """Pragtech GPS Sales Module""",
    "data": [
        'security/user_access.xml',
        'security/ir.model.access.csv',
        'data/crm_lead_sequence.xml',
        'views/crm_lead_inherit_view.xml',
        'views/res_partner_inherit_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/customer_group_view.xml',
        'views/res_config_settings_inherit_view.xml',
        # 'wizard/crm_lead_to_opportunity_wizard.xml',
        'wizard/opportunity_conversion_wizard.xml',
        'wizard/quotation_creation_wizard.xml',
        'wizard/quotation_confirmation_wizard.xml',
        'wizard/sale_order_submit_wizard.xml',
        'wizard/invoice_generation_wizard.xml',
        'report/report_menu.xml',
        'report/report_sale_quotation.xml',
        'report/sale_line_report.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'web/static/lib/jquery/jquery.js',
            'web/static/src/legacy/js/libs/jquery.js',
            'pragtech_GPS_sales/static/src/js/get_location.js',

        ],
    },
    'license': 'OPL-1',
    'installable': True,
    'application': True,
    'auto_install': False,
}
