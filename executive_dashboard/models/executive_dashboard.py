# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta


class ExecutiveDashboard(models.TransientModel):
    _name = 'executive.dashboard'
    _description = 'Executive Dashboard Data'

    @api.model
    def get_company_overview(self, start_date=None, end_date=None):
        """Get overall company performance metrics"""
        today = datetime.now().date()
        if not start_date:
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = today.strftime('%Y-%m-%d')
        
        # Get currency symbol
        company = self.env.company
        currency_symbol = company.currency_id.symbol if company.currency_id else ''
        
        # HR Metrics
        total_employees = self.env['hr.employee'].search_count([('active', '=', True)])
        contracts = self.env['hr.contract'].search([
            ('state', 'in', ['open', 'close']),
            ('date_end', '>=', start_date),
            ('date_end', '<=', end_date)
        ])
        expiring_contracts = len(contracts)
        total_payroll = sum(contracts.mapped('wage')) or 0.0
        
        # Inventory Metrics
        products = self.env['product.product'].search([('type', '!=', 'service')])
        total_products = len(products)
        low_stock_products = len(products.filtered(lambda p: 0 < p.qty_available < 10))
        total_stock_value = sum(products.mapped(lambda p: p.qty_available * p.standard_price)) or 0.0
        
        # Sales Metrics
        sales_orders = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done']),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        total_sales_orders = len(sales_orders)
        total_sales_revenue = sum(sales_orders.mapped('amount_total')) or 0.0
        quotations = self.env['sale.order'].search_count([
            ('state', '=', 'draft'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        
        # Purchase Metrics
        purchase_orders = self.env['purchase.order'].search([
            ('state', 'in', ['purchase', 'done']),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        total_purchase_orders = len(purchase_orders)
        total_purchase_amount = sum(purchase_orders.mapped('amount_total')) or 0.0
        pending_purchases = self.env['purchase.order'].search_count([
            ('state', '=', 'draft'),
            ('date_order', '>=', start_date),
            ('date_order', '<=', end_date)
        ])
        
        # Finance Metrics
        invoices = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date)
        ])
        total_revenue = sum(invoices.filtered(lambda inv: inv.move_type == 'out_invoice').mapped('amount_total')) or 0.0
        total_refunds = sum(invoices.filtered(lambda inv: inv.move_type == 'out_refund').mapped('amount_total')) or 0.0
        net_revenue = total_revenue - total_refunds
        
        bills = self.env['account.move'].search([
            ('move_type', 'in', ['in_invoice', 'in_refund']),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date)
        ])
        total_expenses = sum(bills.filtered(lambda bill: bill.move_type == 'in_invoice').mapped('amount_total')) or 0.0
        
        # Fleet Metrics (if fleet module is installed)
        total_vehicles = 0
        active_vehicles = 0
        try:
            vehicles = self.env['fleet.vehicle'].search([])
            total_vehicles = len(vehicles)
            active_vehicles = len(vehicles.filtered(lambda v: v.state_id and v.state_id.name != 'Written-off'))
        except:
            pass
        
        return {
            # HR
            'total_employees': total_employees,
            'expiring_contracts': expiring_contracts,
            'total_payroll': total_payroll,
            # Inventory
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'total_stock_value': total_stock_value,
            # Sales
            'total_sales_orders': total_sales_orders,
            'total_sales_revenue': total_sales_revenue,
            'quotations': quotations,
            # Purchase
            'total_purchase_orders': total_purchase_orders,
            'total_purchase_amount': total_purchase_amount,
            'pending_purchases': pending_purchases,
            # Finance
            'total_revenue': total_revenue,
            'net_revenue': net_revenue,
            'total_expenses': total_expenses,
            'profit': net_revenue - total_expenses,
            # Fleet
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            # Currency
            'currency_symbol': currency_symbol,
        }

    @api.model
    def get_revenue_vs_expenses(self, start_date=None, end_date=None):
        """Get revenue vs expenses trend for the last 12 months"""
        labels = []
        revenue_data = []
        expenses_data = []
        profit_data = []

        for i in range(11, -1, -1):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Revenue
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', month_start.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', month_end.strftime('%Y-%m-%d'))
            ])
            revenue = sum(invoices.mapped('amount_total')) or 0.0

            # Expenses
            bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', month_start.strftime('%Y-%m-%d')),
                ('invoice_date', '<=', month_end.strftime('%Y-%m-%d'))
            ])
            expenses = sum(bills.mapped('amount_total')) or 0.0

            profit = revenue - expenses

            labels.append(month_date.strftime('%b %Y'))
            revenue_data.append(revenue)
            expenses_data.append(expenses)
            profit_data.append(profit)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Revenue',
                    'data': revenue_data,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'tension': 0.1,
                },
                {
                    'label': 'Expenses',
                    'data': expenses_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1,
                },
                {
                    'label': 'Profit',
                    'data': profit_data,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1,
                },
            ],
        }

    @api.model
    def get_sales_vs_purchase(self, start_date=None, end_date=None):
        """Get sales vs purchase comparison for the last 12 months"""
        labels = []
        sales_data = []
        purchase_data = []

        for i in range(11, -1, -1):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            # Sales
            sales_orders = self.env['sale.order'].search([
                ('state', 'in', ['sale', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d')),
                ('date_order', '<=', month_end.strftime('%Y-%m-%d 23:59:59'))
            ])
            sales = sum(sales_orders.mapped('amount_total')) or 0.0

            # Purchase
            purchase_orders = self.env['purchase.order'].search([
                ('state', 'in', ['purchase', 'done']),
                ('date_order', '>=', month_start.strftime('%Y-%m-%d')),
                ('date_order', '<=', month_end.strftime('%Y-%m-%d 23:59:59'))
            ])
            purchase = sum(purchase_orders.mapped('amount_total')) or 0.0

            labels.append(month_date.strftime('%b %Y'))
            sales_data.append(sales)
            purchase_data.append(purchase)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Sales Revenue',
                    'data': sales_data,
                    'borderColor': 'rgb(54, 162, 235)',
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'tension': 0.1,
                },
                {
                    'label': 'Purchase Amount',
                    'data': purchase_data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1,
                },
            ],
        }

    @api.model
    def get_department_performance(self):
        """Get employee count by department"""
        employees = self.env['hr.employee'].search([('active', '=', True)])
        dept_data = {}

        for emp in employees:
            dept_name = emp.department_id.name if emp.department_id else 'No Department'
            dept_data[dept_name] = dept_data.get(dept_name, 0) + 1

        labels = list(dept_data.keys())
        data = list(dept_data.values())

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Employees per Department',
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

