# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_after_sales_statistics(self, start_date=None, end_date=None):
        """Get after-sales statistics for the dashboard"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("get_after_sales_statistics called with start_date=%s, end_date=%s", start_date, end_date)
            
            # Domain for service orders (orders with repair job cards or service-related products)
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            # Check if repair.order model exists
            has_repair = self.env['ir.model'].search([('model', '=', 'repair.order')], limit=1)
            if has_repair:
                domain.append(('repair_job_card_id', '!=', False))
            
            orders = self.search(domain)
            
            # Also get parts/service orders by checking product categories
            # Common service/parts categories keywords
            service_keywords = ['service', 'repair', 'part', 'spare', 'maintenance', 'warranty']
            parts_domain = [('state', 'in', ['sale', 'done'])]
            if start_date:
                parts_domain.append(('date_order', '>=', start_date))
            if end_date:
                parts_domain.append(('date_order', '<=', end_date))
            
            parts_orders = self.env['sale.order'].search(parts_domain)
            service_line_count = 0
            parts_revenue = 0.0
            
            for order in parts_orders:
                for line in order.order_line:
                    if line.product_id and line.product_id.categ_id:
                        cat_name = (line.product_id.categ_id.name or '').lower()
                        if any(keyword in cat_name for keyword in service_keywords):
                            service_line_count += 1
                            parts_revenue += line.price_subtotal or 0.0
                            if order not in orders:
                                orders |= order
            
            total_service_orders = len(orders)
            total_service_revenue = sum(orders.mapped('amount_total')) or 0.0 + parts_revenue
            
            # Pending service orders (draft/confirmed but not done)
            pending_domain = [('state', 'in', ['draft', 'sale'])]
            if has_repair:
                pending_domain.append(('repair_job_card_id', '!=', False))
            if start_date:
                pending_domain.append(('date_order', '>=', start_date))
            if end_date:
                pending_domain.append(('date_order', '<=', end_date))
            
            pending_orders = len(self.search(pending_domain))
            
            # Completed service orders
            completed_orders = len(self.search([('id', 'in', orders.ids), ('state', '=', 'done')]))
            
            # Average service value
            avg_service_value = total_service_revenue / total_service_orders if total_service_orders > 0 else 0.0
            
            # Count unique customers with service orders
            unique_customers = len(set(orders.mapped('partner_id').ids)) if orders else 0
            
            # Warranty claims (service orders with warranty-related products)
            warranty_keywords = ['warranty', 'guarantee']
            warranty_revenue = 0.0
            warranty_count = 0
            
            for order in orders:
                for line in order.order_line:
                    if line.product_id:
                        product_name = (line.product_id.name or '').lower()
                        cat_name = (line.product_id.categ_id.name or '').lower() if line.product_id.categ_id else ''
                        if any(keyword in product_name or keyword in cat_name for keyword in warranty_keywords):
                            warranty_revenue += line.price_subtotal or 0.0
                            warranty_count += 1
                            break
            
            # Get currency symbol
            try:
                company = self.env.company
                currency_symbol = company.currency_id.symbol if company.currency_id else ''
            except Exception:
                currency_symbol = ''
            
            result = {
                'total_service_orders': total_service_orders,
                'total_service_revenue': total_service_revenue,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'avg_service_value': avg_service_value,
                'total_customers': unique_customers,
                'warranty_claims': warranty_count,
                'parts_revenue': parts_revenue,
                'service_line_count': service_line_count,
                'currency_symbol': currency_symbol,
            }
            _logger.info("Returning after-sales statistics: %s", result)
            return result
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_after_sales_statistics: %s", str(e), exc_info=True)
            return {
                'total_service_orders': 0,
                'total_service_revenue': 0.0,
                'pending_orders': 0,
                'completed_orders': 0,
                'avg_service_value': 0.0,
                'total_customers': 0,
                'warranty_claims': 0,
                'parts_revenue': 0.0,
                'service_line_count': 0,
                'currency_symbol': '',
            }

    @api.model
    def get_monthly_service_trends(self, start_date=None, end_date=None):
        """Get monthly service trends for the last 12 months"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            
            labels = []
            revenue_data = []
            order_count_data = []

            # Get current date and calculate 12 months back
            today = datetime.now().date()
            current_month = today.replace(day=1)
            
            # Check if repair.order model exists
            has_repair = self.env['ir.model'].search([('model', '=', 'repair.order')], limit=1)
            
            for i in range(11, -1, -1):
                month_start = current_month - relativedelta(months=i)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                
                month_label = month_start.strftime('%b %Y')
                month_start_str = month_start.strftime('%Y-%m-%d')
                month_end_str = month_end.strftime('%Y-%m-%d')
                
                domain = [
                    ('state', 'in', ['sale', 'done']),
                    ('date_order', '>=', month_start_str),
                    ('date_order', '<=', month_end_str)
                ]
                
                if has_repair:
                    domain.append(('repair_job_card_id', '!=', False))
                
                orders = self.search(domain)
                
                # Also check for service/parts orders by category
                service_keywords = ['service', 'repair', 'part', 'spare', 'maintenance']
                parts_revenue = 0.0
                for order in orders:
                    for line in order.order_line:
                        if line.product_id and line.product_id.categ_id:
                            cat_name = (line.product_id.categ_id.name or '').lower()
                            if any(keyword in cat_name for keyword in service_keywords):
                                parts_revenue += line.price_subtotal or 0.0
                                break
                
                total_revenue = sum(orders.mapped('amount_total')) or 0.0 + parts_revenue
                order_count = len(orders)

                labels.append(month_label)
                revenue_data.append(float(total_revenue))
                order_count_data.append(int(order_count))

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Service Revenue',
                        'data': revenue_data,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'yAxisID': 'y',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Number of Service Orders',
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
            _logger.error("Error in get_monthly_service_trends: %s", str(e), exc_info=True)
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
                        'label': 'Service Revenue',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'yAxisID': 'y',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Number of Service Orders',
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
    def get_service_type_breakdown(self, start_date=None, end_date=None):
        """Get service breakdown by type (Repair, Maintenance, Parts, Warranty)"""
        try:
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            has_repair = self.env['ir.model'].search([('model', '=', 'repair.order')], limit=1)
            if has_repair:
                domain.append(('repair_job_card_id', '!=', False))
            
            orders = self.search(domain)
            
            service_types = {
                'Repair': 0.0,
                'Maintenance': 0.0,
                'Parts Sales': 0.0,
                'Warranty': 0.0,
                'Other Services': 0.0,
            }
            
            for order in orders:
                order_amount = 0.0
                is_repair = has_repair and order.repair_job_card_id
                is_warranty = False
                is_parts = False
                is_maintenance = False
                
                for line in order.order_line:
                    if line.product_id:
                        product_name = (line.product_id.name or '').lower()
                        cat_name = (line.product_id.categ_id.name or '').lower() if line.product_id.categ_id else ''
                        
                        # Check for warranty
                        if 'warranty' in product_name or 'warranty' in cat_name or 'guarantee' in product_name:
                            is_warranty = True
                            order_amount += line.price_subtotal or 0.0
                        # Check for parts
                        elif any(kw in cat_name or kw in product_name for kw in ['part', 'spare', 'component']):
                            is_parts = True
                            order_amount += line.price_subtotal or 0.0
                        # Check for maintenance
                        elif any(kw in cat_name or kw in product_name for kw in ['maintenance', 'service', 'check']):
                            is_maintenance = True
                            order_amount += line.price_subtotal or 0.0
                        else:
                            order_amount += line.price_subtotal or 0.0
                
                if is_repair:
                    service_types['Repair'] += order_amount
                elif is_warranty:
                    service_types['Warranty'] += order_amount
                elif is_parts:
                    service_types['Parts Sales'] += order_amount
                elif is_maintenance:
                    service_types['Maintenance'] += order_amount
                else:
                    service_types['Other Services'] += order_amount
            
            labels = list(service_types.keys())
            data = list(service_types.values())
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Revenue by Service Type',
                        'data': data,
                        'backgroundColor': [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                        ],
                        'borderColor': [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                        ],
                        'borderWidth': 1,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_service_type_breakdown: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Revenue by Service Type',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

    @api.model
    def get_customer_service_performance(self, start_date=None, end_date=None):
        """Get top customers by service revenue"""
        try:
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            has_repair = self.env['ir.model'].search([('model', '=', 'repair.order')], limit=1)
            if has_repair:
                domain.append(('repair_job_card_id', '!=', False))
            
            orders = self.search(domain)
            
            customer_data = {}
            service_keywords = ['service', 'repair', 'part', 'spare', 'maintenance']
            
            for order in orders:
                try:
                    customer_name = order.partner_id.name if order.partner_id else 'Unknown'
                    
                    # Calculate service revenue for this order
                    order_revenue = order.amount_total or 0.0
                    
                    # Add parts revenue if applicable
                    for line in order.order_line:
                        if line.product_id and line.product_id.categ_id:
                            cat_name = (line.product_id.categ_id.name or '').lower()
                            if any(keyword in cat_name for keyword in service_keywords):
                                order_revenue += line.price_subtotal or 0.0
                    
                    if customer_name not in customer_data:
                        customer_data[customer_name] = 0.0
                    customer_data[customer_name] += order_revenue
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
                        'label': 'Service Revenue by Customer',
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
            _logger.error("Error in get_customer_service_performance: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Service Revenue by Customer',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

    @api.model
    def get_parts_category_sales(self, start_date=None, end_date=None):
        """Get parts sales by product category"""
        try:
            domain = [('state', 'in', ['sale', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            category_data = {}
            parts_keywords = ['part', 'spare', 'component', 'accessory']
            
            for order in orders:
                try:
                    for line in order.order_line:
                        if line.product_id and line.product_id.categ_id:
                            try:
                                category = line.product_id.categ_id.name if line.product_id.categ_id else 'Uncategorized'
                                cat_name_lower = category.lower()
                                
                                # Only include if it's a parts category
                                if any(keyword in cat_name_lower for keyword in parts_keywords):
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
                        'label': 'Parts Sales by Category',
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
            _logger.error("Error in get_parts_category_sales: %s", str(e), exc_info=True)
            return {
                'labels': [],
                'datasets': [
                    {
                        'label': 'Parts Sales by Category',
                        'data': [],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

    @api.model
    def get_collection_forecast(self, start_date=None, end_date=None, forecast_months=12):
        """Get collection forecast for installment payments from car sales
        Returns expected collections for the next N months based on payment terms
        """
        try:
            import logging
            from collections import defaultdict
            _logger = logging.getLogger(__name__)
            
            # Dictionary to store collections by month
            collection_forecast = defaultdict(float)
            
            today = datetime.now().date()
            forecast_end = today + relativedelta(months=forecast_months)
            
            # Get all unpaid invoices (customer invoices) with residual amounts
            # This is the most accurate source for collection forecasts
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('amount_residual', '>', 0),
            ])
            
            _logger.info("Found %d unpaid invoices for collection forecast", len(invoices))
            
            for invoice in invoices:
                try:
                    amount = abs(invoice.amount_residual) or 0.0
                    if amount <= 0:
                        continue
                    
                    # Get due date from invoice
                    due_date = invoice.invoice_date_due
                    if not due_date:
                        # If no due date, use invoice date + payment terms or skip
                        continue
                    
                    # Convert to date if it's a datetime
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()
                    
                    # Only include dates within the forecast period
                    if due_date >= today and due_date <= forecast_end:
                        month_key = due_date.strftime('%Y-%m')
                        collection_forecast[month_key] += amount
                        _logger.debug("Added collection: %s on %s (month: %s) from invoice %s", 
                                    amount, due_date, month_key, invoice.name)
                    elif due_date < today:
                        # Past due collections - add to current month
                        month_key = today.strftime('%Y-%m')
                        collection_forecast[month_key] += amount
                        _logger.debug("Added past due collection: %s on %s (month: %s) from invoice %s", 
                                    amount, due_date, month_key, invoice.name)
                except Exception as e:
                    _logger.warning("Error processing invoice %s for collection forecast: %s", invoice.name, str(e))
                    continue
            
            # Generate labels and data for the next N months
            labels = []
            data = []
            
            for i in range(forecast_months):
                forecast_month = today.replace(day=1) + relativedelta(months=i)
                month_key = forecast_month.strftime('%Y-%m')
                month_label = forecast_month.strftime('%b %Y')
                amount = collection_forecast.get(month_key, 0.0)
                
                labels.append(month_label)
                data.append(float(amount))
            
            # Get currency symbol
            try:
                company = self.env.company
                currency_symbol = company.currency_id.symbol if company.currency_id else ''
            except Exception:
                currency_symbol = ''
            
            _logger.info("Collection forecast generated: %s months, total: %s", 
                        forecast_months, sum(data))
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Expected Collections',
                        'data': data,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
                'currency_symbol': currency_symbol,
                'total_expected': sum(data),
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_collection_forecast: %s", str(e), exc_info=True)
            
            # Return empty forecast
            labels = []
            today = datetime.now().date()
            for i in range(forecast_months):
                forecast_month = today.replace(day=1) + relativedelta(months=i)
                labels.append(forecast_month.strftime('%b %Y'))
            
            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Expected Collections',
                        'data': [0.0] * forecast_months,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
                'currency_symbol': '',
                'total_expected': 0.0,
            }

