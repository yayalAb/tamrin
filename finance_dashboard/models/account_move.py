# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def get_finance_statistics(self, start_date=None, end_date=None):
        """Get financial statistics for the dashboard"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("get_finance_statistics called with start_date=%s, end_date=%s", start_date, end_date)
            
            # Revenue (Customer Invoices)
            invoice_domain = [
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted')
            ]
            if start_date:
                invoice_domain.append(('invoice_date', '>=', start_date))
            if end_date:
                invoice_domain.append(('invoice_date', '<=', end_date))
            
            invoices = self.search(invoice_domain)
            total_revenue = sum(invoices.filtered(lambda inv: inv.move_type == 'out_invoice').mapped('amount_total')) or 0.0
            total_refunds = sum(invoices.filtered(lambda inv: inv.move_type == 'out_refund').mapped('amount_total')) or 0.0
            net_revenue = total_revenue - total_refunds
            
            # Expenses (Vendor Bills)
            bill_domain = [
                ('move_type', 'in', ['in_invoice', 'in_refund']),
                ('state', '=', 'posted')
            ]
            if start_date:
                bill_domain.append(('invoice_date', '>=', start_date))
            if end_date:
                bill_domain.append(('invoice_date', '<=', end_date))
            
            bills = self.search(bill_domain)
            total_expenses = sum(bills.filtered(lambda bill: bill.move_type == 'in_invoice').mapped('amount_total')) or 0.0
            expense_refunds = sum(bills.filtered(lambda bill: bill.move_type == 'in_refund').mapped('amount_total')) or 0.0
            net_expenses = total_expenses - expense_refunds
            
            # Profit
            profit = net_revenue - net_expenses
            
            # Accounts Receivable (Unpaid Customer Invoices)
            ar_domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ]
            ar_invoices = self.search(ar_domain)
            accounts_receivable = sum(ar_invoices.mapped('amount_residual')) or 0.0
            
            # Accounts Payable (Unpaid Vendor Bills)
            ap_domain = [
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial'])
            ]
            ap_bills = self.search(ap_domain)
            accounts_payable = sum(ap_bills.mapped('amount_residual')) or 0.0
            
            # Cash Flow (Paid amounts)
            paid_invoices = invoices.filtered(lambda inv: inv.payment_state == 'paid')
            paid_bills = bills.filtered(lambda bill: bill.payment_state == 'paid')
            cash_inflow = sum(paid_invoices.filtered(lambda inv: inv.move_type == 'out_invoice').mapped('amount_total')) or 0.0
            cash_outflow = sum(paid_bills.filtered(lambda bill: bill.move_type == 'in_invoice').mapped('amount_total')) or 0.0
            net_cash_flow = cash_inflow - cash_outflow
            
            # Invoice counts
            total_invoices = len(invoices.filtered(lambda inv: inv.move_type == 'out_invoice'))
            paid_invoices_count = len(paid_invoices.filtered(lambda inv: inv.move_type == 'out_invoice'))
            unpaid_invoices_count = len(ar_invoices)
            
            # Bill counts
            total_bills = len(bills.filtered(lambda bill: bill.move_type == 'in_invoice'))
            paid_bills_count = len(paid_bills.filtered(lambda bill: bill.move_type == 'in_invoice'))
            unpaid_bills_count = len(ap_bills)
            
            # Get currency symbol
            try:
                company = self.env.company
                currency_symbol = company.currency_id.symbol if company.currency_id else ''
            except Exception:
                currency_symbol = ''
            
            result = {
                'total_revenue': total_revenue,
                'net_revenue': net_revenue,
                'total_expenses': total_expenses,
                'net_expenses': net_expenses,
                'profit': profit,
                'accounts_receivable': accounts_receivable,
                'accounts_payable': accounts_payable,
                'cash_inflow': cash_inflow,
                'cash_outflow': cash_outflow,
                'net_cash_flow': net_cash_flow,
                'total_invoices': total_invoices,
                'paid_invoices_count': paid_invoices_count,
                'unpaid_invoices_count': unpaid_invoices_count,
                'total_bills': total_bills,
                'paid_bills_count': paid_bills_count,
                'unpaid_bills_count': unpaid_bills_count,
                'currency_symbol': currency_symbol,
            }
            _logger.info("Returning finance statistics: %s", result)
            return result
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_finance_statistics: %s", str(e), exc_info=True)
            return {
                'total_revenue': 0.0,
                'net_revenue': 0.0,
                'total_expenses': 0.0,
                'net_expenses': 0.0,
                'profit': 0.0,
                'accounts_receivable': 0.0,
                'accounts_payable': 0.0,
                'cash_inflow': 0.0,
                'cash_outflow': 0.0,
                'net_cash_flow': 0.0,
                'total_invoices': 0,
                'paid_invoices_count': 0,
                'unpaid_invoices_count': 0,
                'total_bills': 0,
                'paid_bills_count': 0,
                'unpaid_bills_count': 0,
                'currency_symbol': '',
            }

    @api.model
    def get_revenue_expenses_trends(self, start_date=None, end_date=None):
        """Get revenue vs expenses trends for the last 12 months"""
        try:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info("get_revenue_expenses_trends called with start_date=%s, end_date=%s", start_date, end_date)
            
            labels = []
            revenue_data = []
            expenses_data = []
            profit_data = []

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
                
                month_start_str = month_start.strftime('%Y-%m-%d')
                month_end_str = month_end.strftime('%Y-%m-%d')
                
                # Revenue
                invoices = self.search([
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', month_start_str),
                    ('invoice_date', '<=', month_end_str)
                ])
                revenue = sum(invoices.filtered(lambda inv: inv.move_type == 'out_invoice').mapped('amount_total')) or 0.0
                refunds = sum(invoices.filtered(lambda inv: inv.move_type == 'out_refund').mapped('amount_total')) or 0.0
                net_revenue = revenue - refunds
                
                # Expenses
                bills = self.search([
                    ('move_type', 'in', ['in_invoice', 'in_refund']),
                    ('state', '=', 'posted'),
                    ('invoice_date', '>=', month_start_str),
                    ('invoice_date', '<=', month_end_str)
                ])
                expenses = sum(bills.filtered(lambda bill: bill.move_type == 'in_invoice').mapped('amount_total')) or 0.0
                expense_refunds = sum(bills.filtered(lambda bill: bill.move_type == 'in_refund').mapped('amount_total')) or 0.0
                net_expenses = expenses - expense_refunds
                
                profit = net_revenue - net_expenses

                labels.append(month_label)
                revenue_data.append(float(net_revenue))
                expenses_data.append(float(net_expenses))
                profit_data.append(float(profit))

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Revenue',
                        'data': revenue_data,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Expenses',
                        'data': expenses_data,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Profit',
                        'data': profit_data,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_revenue_expenses_trends: %s", str(e), exc_info=True)
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
                        'label': 'Revenue',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Expenses',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Profit',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }

    @api.model
    def get_payment_status_breakdown(self, start_date=None, end_date=None):
        """Get payment status breakdown for invoices and bills"""
        try:
            # Invoices
            invoice_domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted')
            ]
            if start_date:
                invoice_domain.append(('invoice_date', '>=', start_date))
            if end_date:
                invoice_domain.append(('invoice_date', '<=', end_date))
            
            invoices = self.search(invoice_domain)
            paid_invoices = invoices.filtered(lambda inv: inv.payment_state == 'paid')
            partial_invoices = invoices.filtered(lambda inv: inv.payment_state == 'partial')
            unpaid_invoices = invoices.filtered(lambda inv: inv.payment_state == 'not_paid')
            
            paid_amount = sum(paid_invoices.mapped('amount_total')) or 0.0
            partial_amount = sum(partial_invoices.mapped('amount_residual')) or 0.0
            unpaid_amount = sum(unpaid_invoices.mapped('amount_total')) or 0.0
            
            # Bills
            bill_domain = [
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted')
            ]
            if start_date:
                bill_domain.append(('invoice_date', '>=', start_date))
            if end_date:
                bill_domain.append(('invoice_date', '<=', end_date))
            
            bills = self.search(bill_domain)
            paid_bills = bills.filtered(lambda bill: bill.payment_state == 'paid')
            partial_bills = bills.filtered(lambda bill: bill.payment_state == 'partial')
            unpaid_bills = bills.filtered(lambda bill: bill.payment_state == 'not_paid')
            
            paid_bills_amount = sum(paid_bills.mapped('amount_total')) or 0.0
            partial_bills_amount = sum(partial_bills.mapped('amount_residual')) or 0.0
            unpaid_bills_amount = sum(unpaid_bills.mapped('amount_total')) or 0.0
            
            return {
                'labels': ['Paid', 'Partial', 'Unpaid'],
                'datasets': [
                    {
                        'label': 'Invoices',
                        'data': [paid_amount, partial_amount, unpaid_amount],
                        'backgroundColor': [
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(255, 99, 132, 0.6)',
                        ],
                        'borderColor': [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                        ],
                        'borderWidth': 1,
                    },
                    {
                        'label': 'Bills',
                        'data': [paid_bills_amount, partial_bills_amount, unpaid_bills_amount],
                        'backgroundColor': [
                            'rgba(75, 192, 192, 0.4)',
                            'rgba(255, 206, 86, 0.4)',
                            'rgba(255, 99, 132, 0.4)',
                        ],
                        'borderColor': [
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(255, 99, 132, 1)',
                        ],
                        'borderWidth': 1,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_payment_status_breakdown: %s", str(e), exc_info=True)
            return {
                'labels': ['Paid', 'Partial', 'Unpaid'],
                'datasets': [
                    {
                        'label': 'Invoices',
                        'data': [0.0, 0.0, 0.0],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                    {
                        'label': 'Bills',
                        'data': [0.0, 0.0, 0.0],
                        'backgroundColor': [],
                        'borderColor': [],
                        'borderWidth': 1,
                    },
                ],
            }

    @api.model
    def get_cash_flow_trends(self, start_date=None, end_date=None):
        """Get cash flow trends for the last 12 months"""
        try:
            labels = []
            inflow_data = []
            outflow_data = []
            net_flow_data = []

            # Get current date and calculate 12 months back
            today = datetime.now().date()
            current_month = today.replace(day=1)
            
            for i in range(11, -1, -1):
                month_start = current_month - relativedelta(months=i)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
                
                month_label = month_start.strftime('%b %Y')
                month_start_str = month_start.strftime('%Y-%m-%d')
                month_end_str = month_end.strftime('%Y-%m-%d')
                
                # Cash Inflow (Paid invoices)
                paid_invoices = self.search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '=', 'paid'),
                    ('invoice_date', '>=', month_start_str),
                    ('invoice_date', '<=', month_end_str)
                ])
                inflow = sum(paid_invoices.mapped('amount_total')) or 0.0
                
                # Cash Outflow (Paid bills)
                paid_bills = self.search([
                    ('move_type', '=', 'in_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '=', 'paid'),
                    ('invoice_date', '>=', month_start_str),
                    ('invoice_date', '<=', month_end_str)
                ])
                outflow = sum(paid_bills.mapped('amount_total')) or 0.0
                
                net_flow = inflow - outflow

                labels.append(month_label)
                inflow_data.append(float(inflow))
                outflow_data.append(float(outflow))
                net_flow_data.append(float(net_flow))

            return {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Cash Inflow',
                        'data': inflow_data,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Cash Outflow',
                        'data': outflow_data,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Net Cash Flow',
                        'data': net_flow_data,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_cash_flow_trends: %s", str(e), exc_info=True)
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
                        'label': 'Cash Inflow',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Cash Outflow',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(255, 99, 132)',
                        'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                    {
                        'label': 'Net Cash Flow',
                        'data': [0.0] * 12,
                        'borderColor': 'rgb(54, 162, 235)',
                        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                        'tension': 0.1,
                        'fill': True,
                        'borderWidth': 2,
                    },
                ],
            }

