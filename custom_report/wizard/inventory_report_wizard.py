# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import timedelta


class InventoryReportWizard(models.TransientModel):
    _name = 'inventory.report.wizard'
    _description = 'Inventory Report Wizard'

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
    product_ids = fields.Many2many(
        'product.product',
        string='Products',
        help='Leave empty to include all products'
    )

    def action_generate_report(self):
        """
        Generate the inventory report
        """
        self.ensure_one()
        
        # Refresh the view
        self.env['inventory.report.summary'].init()
        
        # Build domain with filters
        domain = []
        
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        
        # Get records based on domain
        records = self.env['inventory.report.summary'].search(domain)
        
        # Return PDF report action
        return self.env.ref('custom_report.action_inventory_report').report_action(records)

