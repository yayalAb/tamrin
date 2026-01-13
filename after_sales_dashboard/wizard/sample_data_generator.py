# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta
import random


class SampleDataGenerator(models.TransientModel):
    _name = 'sample.data.generator'
    _description = 'Sample Data Generator for Dashboards'
    
    @api.model
    def generate_sample_data(self):
        """Generate sample data for dashboards - can be called from UI"""
        try:
            env = self.env
            
            # Get or create payment terms
            payment_term_30_70 = env['account.payment.term'].search([
                ('name', '=', '30% Down, 7 Monthly Installments')
            ], limit=1)
            
            if not payment_term_30_70:
                payment_term_30_70 = env['account.payment.term'].create({
                    'name': '30% Down, 7 Monthly Installments',
                })
                # Create payment term lines
                env['account.payment.term.line'].create({
                    'payment_id': payment_term_30_70.id,
                    'value': 'percent',
                    'percent': 30.0,
                    'days': 0,
                    'option': 'day_after_invoice_date',
                    'sequence': 10,
                })
                # Create 7 monthly installments of 10% each
                for i in range(1, 8):
                    env['account.payment.term.line'].create({
                        'payment_id': payment_term_30_70.id,
                        'value': 'percent',
                        'percent': 10.0,
                        'days': 0,
                        'option': 'day_following_month',
                        'sequence': 10 + i,
                    })
            
            # Get standard payment terms
            immediate_payment = env['account.payment.term'].search([
                ('name', 'ilike', 'Immediate')
            ], limit=1)
            
            # Get or create product categories
            car_category = env['product.category'].search([('name', '=', 'Cars')], limit=1)
            if not car_category:
                car_category = env['product.category'].create({'name': 'Cars'})
            
            parts_category = env['product.category'].search([('name', '=', 'Parts & Spares')], limit=1)
            if not parts_category:
                parts_category = env['product.category'].create({'name': 'Parts & Spares'})
            
            service_category = env['product.category'].search([('name', '=', 'Services')], limit=1)
            if not service_category:
                service_category = env['product.category'].create({'name': 'Services'})
            
            warranty_category = env['product.category'].search([('name', '=', 'Warranty')], limit=1)
            if not warranty_category:
                warranty_category = env['product.category'].create({'name': 'Warranty'})
            
            # Get product uom
            unit_uom = env.ref('uom.product_uom_unit', raise_if_not_found=False)
            if not unit_uom:
                unit_uom = env['uom.uom'].search([('name', '=', 'Units')], limit=1)
            
            # Create products
            cars = []
            car_data = [
                ('Toyota Camry 2024', 35000), ('Honda Accord 2024', 32000),
                ('BMW 3 Series', 45000), ('Mercedes C-Class', 48000), ('Audi A4', 42000)
            ]
            
            for name, price in car_data:
                product = env['product.product'].search([
                    ('name', '=', name), ('categ_id', '=', car_category.id)
                ], limit=1)
                if not product:
                    product = env['product.product'].create({
                        'name': name, 'categ_id': car_category.id, 'type': 'product',
                        'sale_ok': True, 'list_price': price,
                        'uom_id': unit_uom.id if unit_uom else False,
                        'uom_po_id': unit_uom.id if unit_uom else False,
                    })
                cars.append(product)
            
            # Create parts
            parts = []
            parts_data = [
                ('Engine Oil Filter', 25), ('Brake Pads Set', 150), ('Air Filter', 30),
                ('Spark Plugs Set', 80), ('Battery', 120), ('Tire Set (4)', 600),
                ('Windshield Wiper', 40), ('Headlight Bulb', 35),
            ]
            
            for name, price in parts_data:
                product = env['product.product'].search([
                    ('name', '=', name), ('categ_id', '=', parts_category.id)
                ], limit=1)
                if not product:
                    product = env['product.product'].create({
                        'name': name, 'categ_id': parts_category.id, 'type': 'product',
                        'sale_ok': True, 'list_price': price,
                        'uom_id': unit_uom.id if unit_uom else False,
                        'uom_po_id': unit_uom.id if unit_uom else False,
                    })
                parts.append(product)
            
            # Create services
            services = []
            services_data = [
                ('Regular Maintenance Service', 150), ('Full Service', 300),
                ('Engine Repair', 800), ('Transmission Service', 450),
                ('AC Service', 200), ('Body Repair', 600),
            ]
            
            for name, price in services_data:
                product = env['product.product'].search([
                    ('name', '=', name), ('categ_id', '=', service_category.id)
                ], limit=1)
                if not product:
                    product = env['product.product'].create({
                        'name': name, 'categ_id': service_category.id, 'type': 'service',
                        'sale_ok': True, 'list_price': price,
                        'uom_id': unit_uom.id if unit_uom else False,
                        'uom_po_id': unit_uom.id if unit_uom else False,
                    })
                services.append(product)
            
            # Create warranty
            warranty = env['product.product'].search([
                ('name', '=', 'Extended Warranty 3 Years'), ('categ_id', '=', warranty_category.id)
            ], limit=1)
            if not warranty:
                warranty = env['product.product'].create({
                    'name': 'Extended Warranty 3 Years', 'categ_id': warranty_category.id,
                    'type': 'service', 'sale_ok': True, 'list_price': 2000,
                    'uom_id': unit_uom.id if unit_uom else False,
                    'uom_po_id': unit_uom.id if unit_uom else False,
                })
            
            # Create customers
            customers = []
            customer_names = [
                'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis',
                'David Wilson', 'Jessica Martinez', 'Robert Taylor', 'Amanda Anderson',
                'Christopher Thomas', 'Michelle Jackson'
            ]
            
            for name in customer_names:
                customer = env['res.partner'].search([
                    ('name', '=', name), ('is_company', '=', False)
                ], limit=1)
                if not customer:
                    customer = env['res.partner'].create({
                        'name': name, 'is_company': False, 'customer_rank': 1,
                    })
                customers.append(customer)
            
            today = datetime.now().date()
            
            # Create sample sale orders (car sales with installments)
            sale_orders = []
            for i in range(15):
                days_ago = random.randint(0, 180)
                order_date = today - timedelta(days=days_ago)
                
                customer = random.choice(customers)
                car = random.choice(cars)
                use_installment = random.random() < 0.7
                
                order = env['sale.order'].create({
                    'partner_id': customer.id,
                    'date_order': datetime.combine(order_date, datetime.min.time()),
                    'payment_term_id': payment_term_30_70.id if use_installment else immediate_payment.id if immediate_payment else False,
                })
                
                env['sale.order.line'].create({
                    'order_id': order.id, 'product_id': car.id,
                    'product_uom_qty': 1, 'price_unit': car.list_price,
                })
                
                if random.random() > 0.3:
                    order.action_confirm()
                    if random.random() > 0.4:
                        order._create_invoices()
                sale_orders.append(order)
            
            # Create sample service orders
            service_orders = []
            for i in range(20):
                days_ago = random.randint(0, 120)
                order_date = today - timedelta(days=days_ago)
                customer = random.choice(customers)
                order_type = random.choice(['parts', 'service', 'warranty', 'mixed'])
                
                order = env['sale.order'].create({
                    'partner_id': customer.id,
                    'date_order': datetime.combine(order_date, datetime.min.time()),
                })
                
                if order_type == 'parts':
                    part = random.choice(parts)
                    env['sale.order.line'].create({
                        'order_id': order.id, 'product_id': part.id,
                        'product_uom_qty': random.randint(1, 4), 'price_unit': part.list_price,
                    })
                elif order_type == 'service':
                    service = random.choice(services)
                    env['sale.order.line'].create({
                        'order_id': order.id, 'product_id': service.id,
                        'product_uom_qty': 1, 'price_unit': service.list_price,
                    })
                elif order_type == 'warranty':
                    env['sale.order.line'].create({
                        'order_id': order.id, 'product_id': warranty.id,
                        'product_uom_qty': 1, 'price_unit': warranty.list_price,
                    })
                else:
                    service = random.choice(services)
                    part = random.choice(parts)
                    env['sale.order.line'].create({
                        'order_id': order.id, 'product_id': service.id,
                        'product_uom_qty': 1, 'price_unit': service.list_price,
                    })
                    env['sale.order.line'].create({
                        'order_id': order.id, 'product_id': part.id,
                        'product_uom_qty': random.randint(1, 3), 'price_unit': part.list_price,
                    })
                
                if random.random() > 0.2:
                    order.action_confirm()
                    if random.random() > 0.3:
                        order._create_invoices()
                service_orders.append(order)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sample Data Generated',
                    'message': f'Successfully generated: {len(cars)} Cars, {len(parts)} Parts, {len(services)} Services, {len(customers)} Customers, {len(sale_orders)} Car Sales, {len(service_orders)} Service Orders',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Error generating sample data: {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

