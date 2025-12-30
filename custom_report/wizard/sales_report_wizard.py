# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import timedelta


class SalesReportWizard(models.TransientModel):
    _name = 'sales.report.wizard'
    _description = 'Sales Report Wizard'

    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today() - timedelta(days=30),
        required=True
    )
    date_to = fields.Date(
        string='Date To',
        default=lambda self: fields.Date.today(),
        required=True
    )
    partner_ids = fields.Many2many(
        'res.partner',
        string='Customers',
        help='Leave empty to include all customers'
    )

    def action_generate_report(self):
        """
        Generate the sales report
        """
        self.ensure_one()
        
        # Refresh the view
        self.env['sales.report.summary'].init()
        
        # Build domain with filters
        domain = []
        
        if self.date_from:
            domain.append(('sale_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('sale_date', '<=', self.date_to))
        if self.partner_ids:
            domain.append(('order_id.partner_id', 'in', self.partner_ids.ids))
        
        # Get records based on domain
        records = self.env['sales.report.summary'].search(domain)
        
        # Return PDF report action
        return self.env.ref('custom_report.action_sales_report').report_action(records)

