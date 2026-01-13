# -*- coding: utf-8 -*-

from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_inventory_statistics(self):
        """Get inventory statistics for the dashboard"""
        # Total products
        total_products = self.search_count([('type', '!=', 'service')])
        
        # Products with stock
        products_with_stock = self.search_count([
            ('type', '!=', 'service'),
            ('qty_available', '>', 0)
        ])
        
        # Low stock products (qty < 10)
        low_stock_products = self.search_count([
            ('type', '!=', 'service'),
            ('qty_available', '>', 0),
            ('qty_available', '<', 10)
        ])
        
        # Out of stock products
        out_of_stock_products = self.search_count([
            ('type', '!=', 'service'),
            ('qty_available', '<=', 0)
        ])
        
        # Total stock value
        products = self.search([('type', '!=', 'service')])
        total_stock_value = sum(products.mapped(lambda p: p.qty_available * p.standard_price)) or 0.0
        
        # Total locations
        locations = self.env['stock.location'].search_count([
            ('usage', '=', 'internal')
        ])
        
        # Get currency symbol
        company = self.env.company
        currency_symbol = company.currency_id.symbol if company.currency_id else ''
        
        return {
            'total_products': total_products,
            'products_with_stock': products_with_stock,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_stock_value': total_stock_value,
            'total_locations': locations,
            'currency_symbol': currency_symbol,
        }

    @api.model
    def get_category_stock(self):
        """Get stock quantity by product category"""
        products = self.search([('type', '!=', 'service')])
        
        category_data = {}
        for product in products:
            category = product.categ_id.name if product.categ_id else 'Uncategorized'
            if category not in category_data:
                category_data[category] = 0.0
            category_data[category] += product.qty_available
        
        # Sort by quantity and get top 8
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:8]
        
        labels = [c[0] for c in sorted_categories]
        data = [c[1] for c in sorted_categories]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Stock Quantity by Category',
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
    def get_category_stock_value(self):
        """Get stock value by product category"""
        products = self.search([('type', '!=', 'service')])
        
        category_data = {}
        for product in products:
            category = product.categ_id.name if product.categ_id else 'Uncategorized'
            if category not in category_data:
                category_data[category] = 0.0
            category_data[category] += product.qty_available * product.standard_price
        
        # Sort by value and get top 8
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)[:8]
        
        labels = [c[0] for c in sorted_categories]
        data = [c[1] for c in sorted_categories]
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Stock Value by Category',
                    'data': data,
                    'backgroundColor': [
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(199, 199, 199, 0.6)',
                        'rgba(83, 102, 255, 0.6)',
                    ],
                    'borderColor': [
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
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
    def get_top_products_by_value(self):
        """Get top products by stock value"""
        products = self.search([
            ('type', '!=', 'service'),
            ('qty_available', '>', 0)
        ], order='qty_available desc', limit=10)
        
        labels = []
        data = []
        
        for product in products:
            product_name = product.name or 'Unknown'
            if len(product_name) > 30:
                product_name = product_name[:27] + '...'
            labels.append(product_name)
            stock_value = product.qty_available * product.standard_price
            data.append(stock_value)
        
        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Stock Value',
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


