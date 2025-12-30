# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def get_monthly_payroll_data(self):
        """Get monthly payroll data for the last 12 months"""
        labels = []
        data = []

        for i in range(11, -1, -1):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            contracts_month = self.search([
                ('state', 'in', ['open', 'close']),
                ('date_start', '<=', month_end.strftime('%Y-%m-%d')),
                '|',
                ('date_end', '>=', month_start.strftime('%Y-%m-%d')),
                ('date_end', '=', False)
            ])

            total_payroll = sum(contracts_month.mapped('wage')) or 0

            labels.append(month_date.strftime('%b'))
            data.append(total_payroll)

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Gross Payroll by Month',
                    'data': data,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'tension': 0.1,
                },
            ],
        }

