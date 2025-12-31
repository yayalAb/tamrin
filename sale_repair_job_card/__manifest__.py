# -*- coding: utf-8 -*-
{
    'name': 'Sale Order Repair Job Card',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Add repair_job_card_id field to sale.order',
    'description': """
        This module adds the repair_job_card_id field to sale.order model
        to fix the undefined field error.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
}

