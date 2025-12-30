# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def get_location_stock(self):
        """Get stock quantity by location"""
        quants = self.search([
            ('location_id.usage', '=', 'internal'),
            ('quantity', '>', 0)
        ])
        
        location_data = {}
        for quant in quants:
            location_name = quant.location_id.complete_name or 'Unknown'
            if location_name not in location_data:
                location_data[location_name] = 0.0
            location_data[location_name] += quant.quantity
        
        # Sort by quantity and get top 10
        sorted_locations = sorted(location_data.items(), key=lambda x: x[1], reverse=True)[:10]
        
        labels = [l[0] for l in sorted_locations]
        data = [l[1] for l in sorted_locations]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Stock Quantity by Location',
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
                        'rgba(255, 99, 255, 0.6)',
                        'rgba(99, 255, 132, 0.6)',
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
                        'rgba(255, 99, 255, 1)',
                        'rgba(99, 255, 132, 1)',
                    ],
                    'borderWidth': 1,
                },
            ],
        }

