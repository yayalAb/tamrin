# -*- coding: utf-8 -*-
{
    'name': 'Custom Sales, Purchase, Inventory & Employee Reports',
    'version': '17.0.1.0.0',
    'category': 'Sales/Purchase/Inventory/HR',
    'summary': 'Custom Reports with Excel-like Format',
    'description': """
        Custom Reports Module
        =====================
        This module provides custom reports:
        
        Sales Report:
        - Serial Number, Part Number, Description, UOM
        - Sold Quantity, Sale Date, Unit Price, Unit Cost
        
        Purchase Report:
        - Serial Number, Part Number, Description, UOM
        - Purchased Quantity, Purchase Date, Unit Price, Unit Cost
        
        Inventory Report:
        - Serial Number, Part Number, Description, UOM
        - All Received Qty, Date of Receipt
        - Sold Qty, Sold Date
        - Remaining Qty, Unit Price, Unit Cost, ABC GROUP
        
        Employee Report:
        - Office, Hiring Date, Education, Edu Level
        - Work Experience at Tamrin, Work Experience Before Tamrin
        - Total Experience, Basic Salary
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['sale', 'sale_management', 'purchase', 'stock', 'account', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_report_view.xml',
        'views/purchase_report_view.xml',
        'views/inventory_report_view.xml',
        'views/employee_report_view.xml',
        'wizard/sales_report_wizard.xml',
        'wizard/purchase_report_wizard.xml',
        'wizard/inventory_report_wizard.xml',
        'wizard/employee_report_wizard.xml',
        'report/sales_report.xml',
        'report/purchase_report.xml',
        'report/inventory_report.xml',
        'report/employee_report.xml',
        'views/sales_report_menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

