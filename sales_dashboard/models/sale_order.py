# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_sales_statistics(self, start_date=None, end_date=None):
        """Get sales statistics for the dashboard"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("get_sales_statistics called with start_date=%s, end_date=%s", start_date, end_date)
            
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            _logger.info("Search domain: %s", domain)
            orders = self.search(domain)
            _logger.info("Found %d orders", len(orders))
            
            total_orders = len(orders)
            total_amount = sum(orders.mapped('amount_total')) or 0.0
            
            # Quotation (draft) and confirmed orders with same date filter
            quotation_domain = [('state', '=', 'draft')]
            confirmed_domain = [('state', '=', 'sale')]
            if start_date:
                quotation_domain.append(('date_order', '>=', start_date))
                confirmed_domain.append(('date_order', '>=', start_date))
            if end_date:
                quotation_domain.append(('date_order', '<=', end_date))
                confirmed_domain.append(('date_order', '<=', end_date))
            
            quotation_orders = len(self.search(quotation_domain))
            confirmed_orders = len(self.search(confirmed_domain))
            
            # Average order value
            avg_order_value = total_amount / total_orders if total_orders > 0 else 0.0
            
            # Count unique customers
            unique_customers = len(set(orders.mapped('partner_id').ids)) if orders else 0
            
            # Get currency symbol
            try:
                company = self.env.company
                currency_symbol = company.currency_id.symbol if company.currency_id else ''
            except Exception:
                currency_symbol = ''
            
            result = {
                'total_orders': total_orders,
                'total_amount': total_amount,
                'quotation_orders': quotation_orders,
                'confirmed_orders': confirmed_orders,
                'avg_order_value': avg_order_value,
                'total_customers': unique_customers,
                'currency_symbol': currency_symbol,
            }
            _logger.info("Returning statistics: %s", result)
            return result
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_sales_statistics: %s", str(e), exc_info=True)
            return {
                'total_orders': 0,
                'total_amount': 0.0,
                'quotation_orders': 0,
                'confirmed_orders': 0,
                'avg_order_value': 0.0,
                'total_customers': 0,
                'currency_symbol': '',
            }

    @api.model
    def get_monthly_sales_trends(self, start_date=None, end_date=None):
        """Get monthly sales trends for the last 12 months"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("get_monthly_sales_trends called with start_date=%s, end_date=%s", start_date, end_date)
            
            # Test: Check if there are any sales orders at all
            all_orders = self.search([('state', 'in', ['sale', 'done'])], limit=5)
            _logger.info("Total sales orders found (sample): %d", len(all_orders))
            if all_orders:
                for order in all_orders:
                    _logger.info("Sample order: id=%s, date_order=%s, state=%s, amount_total=%s", 
                               order.id, order.date_order, order.state, order.amount_total)
            else:
                _logger.warning("No sales orders found with state 'sale' or 'done'!")
            
            labels = []
            amount_data = []
            order_count_data = []

            # Get current date and calculate 12 months back
            today = datetime.now().date()
            current_month = today.replace(day=1)
            
            for i in range(11, -1, -1):
                # Calculate month by going back i months from current month
                month_start = current_month - relativedelta(months=i)
                # Calculate last day of month
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                
                # Format month label
                month_label = month_start.strftime('%b %Y')

                try:
                    # Use date format for search (Odoo handles datetime fields with date strings)
                    month_start_str = month_start.strftime('%Y-%m-%d')
                    month_end_str = month_end.strftime('%Y-%m-%d')
                    
                    domain = [
                        ('state', 'in', ['sale', 'done']),
                        ('date_order', '>=', month_start_str),
                        ('date_order', '<=', month_end_str)
                    ]

                    _logger.info("Month %s: Searching with domain %s", month_label, domain)
                    orders = self.search(domain)
                    total_amount = sum(orders.mapped('amount_total')) or 0.0
                    order_count = len(orders)
                    _logger.info("Month %s: Found %d orders, total amount: %s", 
                               month_label, order_count, total_amount)
                    
                    # Debug: Show first order details if found
                    if orders and order_count > 0:
                        _logger.info("First order in month: date_order=%s, amount_total=%s", 
                                   orders[0].date_order, orders[0].amount_total)
                except Exception as e:
                    _logger.error("Error calculating data for month %s: %s", 
                                month_label, str(e), exc_info=True)
                    total_amount = 0.0
                    order_count = 0

                labels.append(month_label)
                amount_data.append(float(total_amount))
                order_count_data.append(int(order_count))

            # Log summary of all data
            _logger.info("Monthly trends summary - Total months: %d, Total amount sum: %s, Total orders sum: %d", 
                        len(labels), sum(amount_data), sum(order_count_data))
            _logger.info("Amount data: %s", amount_data)
            _logger.info("Order count data: %s", order_count_data)

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales Amount',
                        'data': amount_data,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'yAxisID': 'y',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Number of Orders',
                        'data': order_count_data,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'yAxisID': 'y1',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_monthly_sales_trends: %s", str(e), exc_info=True)
            # Return empty data structure
            default_labels = []
            today = datetime.now().date()
            current_month = today.replace(day=1)
            for i in range(11, -1, -1):
                month_start = current_month - relativedelta(months=i)
                default_labels.append(month_start.strftime('%b %Y'))
            return {
                'labels': default_labels,
                'datasets': [
                    {
                        'label': 'Sales Amount',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'yAxisID': 'y',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Number of Orders',
                        'data': [0] * 12,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'yAxisID': 'y1',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }

    @api.model
    def get_customer_performance(self, start_date=None, end_date=None):
        """Get top customers by sales amount"""
        try:
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            customer_data = {}
            for order in orders:
                try:
                    customer_name = order.partner_id.name if order.partner_id else 'Unknown'
                    if customer_name not in customer_data:
                        customer_data[customer_name] = 0.0
                    customer_data[customer_name] += order.amount_total or 0.0
                except Exception:
                    continue
            
            # Sort by amount and get top 10
            sorted_customers = sorted(customer_data.items(), key=lambda x: x[1], reverse=True)[:10]
            
            labels = [c[0] for c in sorted_customers]
            data = [c[1] for c in sorted_customers]
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales Amount by Customer',
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
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_customer_performance: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Sales Amount by Customer',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

    @api.model
    def get_category_sales(self, start_date=None, end_date=None):
        """Get sales by product category"""
        try:
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            category_data = {}
            for order in orders:
                try:
                    for line in order.order_line:
                        try:
                            category = line.product_id.categ_id.name if (line.product_id and line.product_id.categ_id) else 'Uncategorized'
                            if category not in category_data:
                                category_data[category] = 0.0
                            category_data[category] += line.price_subtotal or 0.0
                        except Exception:
                            continue
                except Exception:
                    continue
            
            # Sort by amount and get top 8
            sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:8]
            
            labels = [c[0] for c in sorted_categories]
            data = [c[1] for c in sorted_categories]
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Sales by Category',
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
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_category_sales: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Sales by Category',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

