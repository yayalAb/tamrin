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

    @api.model
    def get_purchase_by_type(self, start_date=None, end_date=None):
        """Get purchase breakdown by type (Local vs Foreign)"""
        try:
            domain = [('state', 'in', ['purchase', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            local_amount = 0.0
            foreign_amount = 0.0
            local_count = 0
            foreign_count = 0
            
            company = self.env.company
            company_country = company.country_id.id if company.country_id else False
            
            for order in orders:
                vendor_country = order.partner_id.country_id.id if order.partner_id and order.partner_id.country_id else False
                amount = order.amount_total or 0.0
                
                if vendor_country == company_country or not vendor_country:
                    local_amount += amount
                    local_count += 1
                else:
                    foreign_amount += amount
                    foreign_count += 1
            
            return {
                'labels': ['Local', 'Foreign'],
                'datasets': [
                    {
                        'label': 'Purchase Amount by Type',
                        'data': [local_amount, foreign_amount],
                        'backgroundColor': [
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                        ],
                        'borderColor': [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 99, 132, 1)',
                        ],
                        'borderWidth': 1,
                    },
                ],
                'local_amount': local_amount,
                'foreign_amount': foreign_amount,
                'local_count': local_count,
                'foreign_count': foreign_count,
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_purchase_by_type: %s", str(e))
            return {
                'labels': ['Local', 'Foreign'],
                'datasets': [
                    {
                        'label': 'Purchase Amount by Type',
                        'data': [0.0, 0.0],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
                'local_amount': 0.0,
                'foreign_amount': 0.0,
                'local_count': 0,
                'foreign_count': 0,
            }

    @api.model
    def get_urgent_purchases(self, start_date=None, end_date=None):
        """Get urgent purchase orders count and amount"""
        try:
            domain = [('state', 'in', ['purchase', 'done', 'draft'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            urgent_orders = []
            urgent_amount = 0.0
            
            today = datetime.now().date()
            
            for order in orders:
                is_urgent = False
                
                if hasattr(order, 'priority') and order.priority:
                    if str(order.priority) in ['1', 'urgent', 'Urgent']:
                        is_urgent = True
                
                if hasattr(order, 'date_planned') and order.date_planned:
                    try:
                        if isinstance(order.date_planned, str):
                            planned_date = datetime.strptime(order.date_planned.split()[0], '%Y-%m-%d').date()
                        elif isinstance(order.date_planned, datetime):
                            planned_date = order.date_planned.date()
                        else:
                            planned_date = order.date_planned
                        
                        days_until = (planned_date - today).days
                        if 0 <= days_until <= 7:
                            is_urgent = True
                    except Exception:
                        pass
                
                if is_urgent:
                    urgent_orders.append(order)
                    urgent_amount += order.amount_total or 0.0
            
            return {
                'count': len(urgent_orders),
                'amount': urgent_amount,
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_urgent_purchases: %s", str(e))
            return {
                'count': 0,
                'amount': 0.0,
            }

    @api.model
    def get_sensitive_data_purchases(self, start_date=None, end_date=None):
        """Get purchases with sensitive/confidential data"""
        try:
            domain = [('state', 'in', ['purchase', 'done', 'draft'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            sensitive_count = 0
            sensitive_amount = 0.0
            
            sensitive_keywords = ['confidential', 'sensitive', 'restricted', 'classified', 'security', 'private']
            
            for order in orders:
                is_sensitive = False
                
                order_text = ''
                if hasattr(order, 'notes') and order.notes:
                    order_text += (order.notes or '').lower()
                if hasattr(order, 'name') and order.name:
                    order_text += (order.name or '').lower()
                if hasattr(order, 'origin') and order.origin:
                    order_text += (order.origin or '').lower()
                
                if any(keyword in order_text for keyword in sensitive_keywords):
                    is_sensitive = True
                
                if not is_sensitive:
                    for line in order.order_line:
                        if line.product_id:
                            product_name = (line.product_id.name or '').lower()
                            if any(keyword in product_name for keyword in sensitive_keywords):
                                is_sensitive = True
                                break
                
                if is_sensitive:
                    sensitive_count += 1
                    sensitive_amount += order.amount_total or 0.0
            
            return {
                'count': sensitive_count,
                'amount': sensitive_amount,
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_sensitive_data_purchases: %s", str(e))
            return {
                'count': 0,
                'amount': 0.0,
            }

    @api.model
    def get_delay_period_data(self, start_date=None, end_date=None):
        """Get purchase orders with delays (overdue deliveries)"""
        try:
            today = datetime.now().date()
            domain = [('state', 'in', ['purchase', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            delay_ranges = {
                '0-7 days': 0,
                '8-15 days': 0,
                '16-30 days': 0,
                '31+ days': 0,
            }
            
            delay_amounts = {
                '0-7 days': 0.0,
                '8-15 days': 0.0,
                '16-30 days': 0.0,
                '31+ days': 0.0,
            }
            
            total_delayed = 0
            total_delay_amount = 0.0
            
            for order in orders:
                if hasattr(order, 'date_planned') and order.date_planned:
                    try:
                        if isinstance(order.date_planned, str):
                            planned_date = datetime.strptime(order.date_planned.split()[0], '%Y-%m-%d').date()
                        elif isinstance(order.date_planned, datetime):
                            planned_date = order.date_planned.date()
                        else:
                            planned_date = order.date_planned
                        
                        if planned_date < today:
                            delay_days = (today - planned_date).days
                            amount = order.amount_total or 0.0
                            
                            if delay_days <= 7:
                                delay_ranges['0-7 days'] += 1
                                delay_amounts['0-7 days'] += amount
                            elif delay_days <= 15:
                                delay_ranges['8-15 days'] += 1
                                delay_amounts['8-15 days'] += amount
                            elif delay_days <= 30:
                                delay_ranges['16-30 days'] += 1
                                delay_amounts['16-30 days'] += amount
                            else:
                                delay_ranges['31+ days'] += 1
                                delay_amounts['31+ days'] += amount
                            
                            total_delayed += 1
                            total_delay_amount += amount
                    except Exception:
                        continue
            
            labels = list(delay_ranges.keys())
            count_data = list(delay_ranges.values())
            amount_data = list(delay_amounts.values())
            
            return {
                'labels': labels,
                'count_data': count_data,
                'amount_data': amount_data,
                'total_delayed': total_delayed,
                'total_delay_amount': total_delay_amount,
                'datasets': [
                    {
                        'label': 'Delayed Orders Count',
                        'data': count_data,
                        'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                        'borderColor': 'rgba(255, 99, 132, 1)',
                        'borderWidth': 1,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_delay_period_data: %s", str(e))
            return {
                'labels': [],
                'count_data': [],
                'amount_data': [],
                'total_delayed': 0,
                'total_delay_amount': 0.0,
                'datasets': [],
            }

    @api.model
    def get_economic_order_quantity(self, start_date=None, end_date=None):
        """Calculate Economic Order Quantity (EOQ) analysis"""
        try:
            domain = [('state', 'in', ['purchase', 'done'])]
            
            if start_date:
                domain.append(('date_order', '>=', start_date))
            if end_date:
                domain.append(('date_order', '<=', end_date))
            
            orders = self.search(domain)
            
            product_data = {}
            ordering_cost_per_order = 50.0
            holding_cost_rate = 0.20
            
            for order in orders:
                for line in order.order_line:
                    if line.product_id:
                        product_id = line.product_id.id
                        if product_id not in product_data:
                            product_data[product_id] = {
                                'total_qty': 0.0,
                                'total_cost': 0.0,
                                'order_count': 0,
                                'avg_price': 0.0,
                            }
                        
                        product_data[product_id]['total_qty'] += line.product_qty or 0.0
                        product_data[product_id]['total_cost'] += (line.price_subtotal or 0.0)
                        product_data[product_id]['order_count'] += 1
            
            eoq_data = []
            for product_id, data in list(product_data.items())[:20]:
                if data['order_count'] > 0:
                    avg_qty_per_order = data['total_qty'] / data['order_count']
                    avg_price = data['total_cost'] / data['total_qty'] if data['total_qty'] > 0 else 0.0
                    
                    annual_demand = data['total_qty']
                    holding_cost_per_unit = avg_price * holding_cost_rate
                    
                    if holding_cost_per_unit > 0:
                        eoq = (2 * annual_demand * ordering_cost_per_order / holding_cost_per_unit) ** 0.5
                    else:
                        eoq = 0.0
                    
                    product = self.env['product.product'].browse(product_id)
                    eoq_data.append({
                        'product_name': product.name or 'Unknown',
                        'current_avg_order_qty': round(avg_qty_per_order, 2),
                        'calculated_eoq': round(eoq, 2),
                        'annual_demand': round(annual_demand, 2),
                    })
            
            eoq_data.sort(key=lambda x: x['annual_demand'], reverse=True)
            
            return {
                'summary': {
                    'total_products_analyzed': len(eoq_data),
                    'avg_eoq': sum(d['calculated_eoq'] for d in eoq_data) / len(eoq_data) if eoq_data else 0.0,
                },
                'top_products': eoq_data[:10],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_economic_order_quantity: %s", str(e))
            return {
                'summary': {
                    'total_products_analyzed': 0,
                    'avg_eoq': 0.0,
                },
                'top_products': [],
            }

