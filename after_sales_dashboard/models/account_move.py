# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_service_revenue_by_status(self, start_date=None, end_date=None):
        """Get service revenue breakdown by invoice status"""
        try:
            domain = [('move_type', '=', 'out_invoice')]
            
            if start_date:
                domain.append(('invoice_date', '>=', start_date))
            if end_date:
                domain.append(('invoice_date', '<=', end_date))
            
            invoices = self.search(domain)
            
            # Filter for service-related invoices (linked to sale orders with repair or service products)
            service_keywords = ['service', 'repair', 'part', 'spare', 'maintenance', 'warranty']
            service_invoices = self.env['account.move']
            
            for invoice in invoices:
                # Check if invoice is linked to sale orders with service products
                if invoice.invoice_origin:
                    sale_orders = self.env['sale.order'].search([
                        ('name', 'in', invoice.invoice_origin.split(', '))
                    ])
                    for order in sale_orders:
                        # Check for repair job card
                        if hasattr(order, 'repair_job_card_id') and order.repair_job_card_id:
                            service_invoices |= invoice
                            break
                        # Check for service-related products
                        for line in order.order_line:
                            if line.product_id:
                                product_name = (line.product_id.name or '').lower()
                                cat_name = (line.product_id.categ_id.name or '').lower() if line.product_id.categ_id else ''
                                if any(keyword in product_name or keyword in cat_name for keyword in service_keywords):
                                    service_invoices |= invoice
                                    break
                        if invoice in service_invoices:
                            break
            
            status_data = {
                'Draft': 0.0,
                'Posted': 0.0,
                'Paid': 0.0,
            }
            
            for invoice in service_invoices:
                amount = invoice.amount_total or 0.0
                if invoice.state == 'draft':
                    status_data['Draft'] += amount
                elif invoice.state == 'posted' and invoice.payment_state == 'not_paid':
                    status_data['Posted'] += amount
                elif invoice.payment_state in ['paid', 'partial']:
                    status_data['Paid'] += amount
            
            labels = list(status_data.keys())
            data = list(status_data.values())
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Service Revenue by Invoice Status',
                        'data': data,
                        'backgroundColor': [
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                        ],
                        'borderColor': [
                            'rgba(255, 206, 86, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                        ],
                        'borderWidth': 1,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_service_revenue_by_status: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Service Revenue by Invoice Status',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

