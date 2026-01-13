# -*- coding: utf-8 -*-
"""
Sample Data Generator for After Sales Dashboard
This script generates sample data to populate the dashboards with realistic data

Usage:
    python odoo-bin shell -d your_database < generate_sample_data.py
    OR
    Run this script from Odoo shell using: exec(open('after_sales_dashboard/demo/generate_sample_data.py').read())
"""

from odoo import api, SUPERUSER_ID
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import random


def generate_sample_data(env):
    """Generate sample data for after sales dashboard"""
    
    # Get or create payment terms
    # 30% down, 70% in monthly installments (7 payments of 10% each)
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
    # Car Category
    car_category = env['product.category'].search([
        ('name', '=', 'Cars')
    ], limit=1)
    if not car_category:
        car_category = env['product.category'].create({
            'name': 'Cars',
        })
    
    # Parts Category
    parts_category = env['product.category'].search([
        ('name', '=', 'Parts & Spares')
    ], limit=1)
    if not parts_category:
        parts_category = env['product.category'].create({
            'name': 'Parts & Spares',
        })
    
    # Service Category
    service_category = env['product.category'].search([
        ('name', '=', 'Services')
    ], limit=1)
    if not service_category:
        service_category = env['product.category'].create({
            'name': 'Services',
        })
    
    # Warranty Category
    warranty_category = env['product.category'].search([
        ('name', '=', 'Warranty')
    ], limit=1)
    if not warranty_category:
        warranty_category = env['product.category'].create({
            'name': 'Warranty',
        })
    
    # Get product uom
    unit_uom = env.ref('uom.product_uom_unit', raise_if_not_found=False)
    if not unit_uom:
        unit_uom = env['uom.uom'].search([('name', '=', 'Units')], limit=1)
    
    # Get or create products
    # Sample Cars
    cars = []
    car_names = ['Toyota Camry 2024', 'Honda Accord 2024', 'BMW 3 Series', 'Mercedes C-Class', 'Audi A4']
    car_prices = [35000, 32000, 45000, 48000, 42000]
    
    for name, price in zip(car_names, car_prices):
        product = env['product.product'].search([
            ('name', '=', name),
            ('categ_id', '=', car_category.id)
        ], limit=1)
        if not product:
            product = env['product.product'].create({
                'name': name,
                'categ_id': car_category.id,
                'type': 'product',
                'sale_ok': True,
                'list_price': price,
                'uom_id': unit_uom.id if unit_uom else False,
                'uom_po_id': unit_uom.id if unit_uom else False,
            })
        cars.append(product)
    
    # Sample Parts
    parts = []
    parts_data = [
        ('Engine Oil Filter', 25),
        ('Brake Pads Set', 150),
        ('Air Filter', 30),
        ('Spark Plugs Set', 80),
        ('Battery', 120),
        ('Tire Set (4)', 600),
        ('Windshield Wiper', 40),
        ('Headlight Bulb', 35),
    ]
    
    for name, price in parts_data:
        product = env['product.product'].search([
            ('name', '=', name),
            ('categ_id', '=', parts_category.id)
        ], limit=1)
        if not product:
            product = env['product.product'].create({
                'name': name,
                'categ_id': parts_category.id,
                'type': 'product',
                'sale_ok': True,
                'list_price': price,
                'uom_id': unit_uom.id if unit_uom else False,
                'uom_po_id': unit_uom.id if unit_uom else False,
            })
        parts.append(product)
    
    # Sample Services
    services = []
    services_data = [
        ('Regular Maintenance Service', 150),
        ('Full Service', 300),
        ('Engine Repair', 800),
        ('Transmission Service', 450),
        ('AC Service', 200),
        ('Body Repair', 600),
    ]
    
    for name, price in services_data:
        product = env['product.product'].search([
            ('name', '=', name),
            ('categ_id', '=', service_category.id)
        ], limit=1)
        if not product:
            product = env['product.product'].create({
                'name': name,
                'categ_id': service_category.id,
                'type': 'service',
                'sale_ok': True,
                'list_price': price,
                'uom_id': unit_uom.id if unit_uom else False,
                'uom_po_id': unit_uom.id if unit_uom else False,
            })
        services.append(product)
    
    # Sample Warranty
    warranty = env['product.product'].search([
        ('name', '=', 'Extended Warranty 3 Years'),
        ('categ_id', '=', warranty_category.id)
    ], limit=1)
    if not warranty:
        warranty = env['product.product'].create({
            'name': 'Extended Warranty 3 Years',
            'categ_id': warranty_category.id,
            'type': 'service',
            'sale_ok': True,
            'list_price': 2000,
            'uom_id': unit_uom.id if unit_uom else False,
            'uom_po_id': unit_uom.id if unit_uom else False,
        })
    
    # Get or create customers
    customers = []
    customer_names = [
        'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis',
        'David Wilson', 'Jessica Martinez', 'Robert Taylor', 'Amanda Anderson',
        'Christopher Thomas', 'Michelle Jackson'
    ]
    
    for name in customer_names:
        customer = env['res.partner'].search([
            ('name', '=', name),
            ('is_company', '=', False)
        ], limit=1)
        if not customer:
            customer = env['res.partner'].create({
                'name': name,
                'is_company': False,
                'customer_rank': 1,
            })
        customers.append(customer)
    
    # Get company
    company = env.company
    today = datetime.now().date()
    
    # Create sample sale orders (car sales with installments)
    sale_orders = []
    for i in range(15):
        days_ago = random.randint(0, 180)  # Last 6 months
        order_date = today - timedelta(days=days_ago)
        
        customer = random.choice(customers)
        car = random.choice(cars)
        
        # 70% of orders use installment payment
        use_installment = random.random() < 0.7
        
        order = env['sale.order'].create({
            'partner_id': customer.id,
            'date_order': datetime.combine(order_date, datetime.min.time()),
            'payment_term_id': payment_term_30_70.id if use_installment else immediate_payment.id if immediate_payment else False,
        })
        
        env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': car.id,
            'product_uom_qty': 1,
            'price_unit': car.list_price,
        })
        
        # Confirm some orders
        if random.random() > 0.3:  # 70% confirmed
            order.action_confirm()
            # Create invoice for some confirmed orders
            if random.random() > 0.4:  # 60% of confirmed orders have invoices
                order._create_invoices()
        sale_orders.append(order)
    
    # Create sample service orders (after sales)
    service_orders = []
    for i in range(20):
        days_ago = random.randint(0, 120)  # Last 4 months
        order_date = today - timedelta(days=days_ago)
        
        customer = random.choice(customers)
        
        # Mix of parts and services
        order_type = random.choice(['parts', 'service', 'warranty', 'mixed'])
        
        order = env['sale.order'].create({
            'partner_id': customer.id,
            'date_order': datetime.combine(order_date, datetime.min.time()),
        })
        
        if order_type == 'parts':
            # Parts order
            part = random.choice(parts)
            qty = random.randint(1, 4)
            env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': part.id,
                'product_uom_qty': qty,
                'price_unit': part.list_price,
            })
        elif order_type == 'service':
            # Service order
            service = random.choice(services)
            env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': service.id,
                'product_uom_qty': 1,
                'price_unit': service.list_price,
            })
        elif order_type == 'warranty':
            # Warranty claim
            env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': warranty.id,
                'product_uom_qty': 1,
                'price_unit': warranty.list_price,
            })
        else:
            # Mixed order
            service = random.choice(services)
            part = random.choice(parts)
            env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': service.id,
                'product_uom_qty': 1,
                'price_unit': service.list_price,
            })
            env['sale.order.line'].create({
                'order_id': order.id,
                'product_id': part.id,
                'product_uom_qty': random.randint(1, 3),
                'price_unit': part.list_price,
            })
        
        # Confirm most service orders
        if random.random() > 0.2:  # 80% confirmed
            order.action_confirm()
            # Create invoice for some
            if random.random() > 0.3:  # 70% have invoices
                order._create_invoices()
        service_orders.append(order)
    
    print(f"Sample data generated successfully!")
    print(f"- {len(cars)} Cars")
    print(f"- {len(parts)} Parts")
    print(f"- {len(services)} Services")
    print(f"- {len(customers)} Customers")
    print(f"- {len(sale_orders)} Car Sales Orders")
    print(f"- {len(service_orders)} Service Orders")
    print(f"- Payment Term: {payment_term_30_70.name if payment_term_30_70 else 'Created'}")
    
    return {
        'cars': cars,
        'parts': parts,
        'services': services,
        'customers': customers,
        'sale_orders': sale_orders,
        'service_orders': service_orders,
    }


# If running as script
if __name__ == '__main__':
    # This would be called from Odoo shell
    # In Odoo shell: exec(open('after_sales_dashboard/demo/generate_sample_data.py').read())
    pass

