# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def get_purchase_statistics(self, start_date=None, end_date=None):
        """Get purchase statistics for the dashboard"""
        domain = [('state', 'in', ['purchase', 'done'])]
        
        if start_date:
            domain.append(('date_order', '>=', start_date))
        if end_date:
            domain.append(('date_order', '<=', end_date))
        
        orders = self.search(domain)
        
        total_orders = len(orders)
        total_amount = sum(orders.mapped('amount_total')) or 0.0
        
        # Pending and approved orders with same date filter
        pending_domain = [('state', '=', 'draft')]
        approved_domain = [('state', '=', 'purchase')]
        if start_date:
            pending_domain.append(('date_order', '>=', start_date))
            approved_domain.append(('date_order', '>=', start_date))
        if end_date:
            pending_domain.append(('date_order', '<=', end_date))
            approved_domain.append(('date_order', '<=', end_date))
        
        pending_orders = len(self.search(pending_domain))
        approved_orders = len(self.search(approved_domain))
        
        # Average order value
        avg_order_value = total_amount / total_orders if total_orders > 0 else 0.0
        
        # Count unique vendors
        unique_vendors = len(orders.mapped('partner_id')) if orders else 0
        
        # Get currency symbol
        company = self.env.company
        currency_symbol = company.currency_id.symbol if company.currency_id else ''
        
        return {
            'total_orders': total_orders,
            'total_amount': total_amount,
            'pending_orders': pending_orders,
            'approved_orders': approved_orders,
            'avg_order_value': avg_order_value,
            'total_vendors': unique_vendors,
            'currency_symbol': currency_symbol,
        }

    @api.model
    def get_monthly_purchase_trends(self, start_date=None, end_date=None):
        """Get monthly purchase trends for the last 12 months"""
        labels = []
        amount_data = []
        order_count_data = []

        for i in range(11, -1, -1):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            domain = [
                ('state', 'in', ['purchase', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d')),
                ('date_order', '<=', month_end.strftime('%Y-%m-%d 23:59:59'))
            ]

            orders = self.search(domain)
            total_amount = sum(orders.mapped('amount_total')) or 0.0
            order_count = len(orders)

            labels.append(month_date.strftime('%b %Y'))
            amount_data.append(total_amount)
            order_count_data.append(order_count)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Purchase Amount',
                    'data': amount_data,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'yAxisID': 'y',
                    'tension': 0.1,
                },
                {
                    'label': 'Number of Orders',
                    'data': order_count_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'yAxisID': 'y1',
                    'tension': 0.1,
                },
            ],
        }

    @api.model
    def get_vendor_performance(self, start_date=None, end_date=None):
        """Get top vendors by purchase amount"""
        domain = [('state', 'in', ['purchase', 'done'])]
        
        if start_date:
            domain.append(('date_order', '>=', start_date))
        if end_date:
            domain.append(('date_order', '<=', end_date))
        
        orders = self.search(domain)
        
        vendor_data = {}
        for order in orders:
            vendor_name = order.partner_id.name or 'Unknown'
            if vendor_name not in vendor_data:
                vendor_data[vendor_name] = 0.0
            vendor_data[vendor_name] += order.amount_total
        
        # Sort by amount and get top 10
        sorted_vendors = sorted(vendor_data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        labels = [v[0] for v in sorted_vendors]
        data = [v[1] for v in sorted_vendors]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Purchase Amount by Vendor',
                    'data': data,
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(199, 199, 199, 0.6)',
                        'rgba(83, 102, 255, 0.6)',
                        'rgba(255, 99, 255, 0.6)',
                        'rgba(99, 255, 132, 0.6)',
                    ],
                    'borderColor': [
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)',
                        'rgba(83, 102, 255, 1)',
                        'rgba(255, 99, 255, 1)',
                        'rgba(99, 255, 132, 1)',
                    ],
                    'borderWidth': 1,
                },
            ],
        }

    @api.model
    def get_category_spending(self, start_date=None, end_date=None):
        """Get spending by product category"""
        domain = [('state', 'in', ['purchase', 'done'])]
        
        if start_date:
            domain.append(('date_order', '>=', start_date))
        if end_date:
            domain.append(('date_order', '<=', end_date))
        
        orders = self.search(domain)
        
        category_data = {}
        for order in orders:
            for line in order.order_line:
                category = line.product_id.categ_id.name if line.product_id.categ_id else 'Uncategorized'
                if category not in category_data:
                    category_data[category] = 0.0
                category_data[category] += line.price_subtotal
        
        # Sort by amount and get top 8
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:8]
        
        labels = [c[0] for c in sorted_categories]
        data = [c[1] for c in sorted_categories]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Spending by Category',
                    'data': data,
                    'backgroundColor': [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(199, 199, 199, 0.6)',
                        'rgba(83, 102, 255, 0.6)',
                    ],
                    'borderColor': [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)',
                        'rgba(83, 102, 255, 1)',
                    ],
                    'borderWidth': 1,
                },
            ],
        }

