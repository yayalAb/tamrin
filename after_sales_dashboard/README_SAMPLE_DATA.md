# Sample Data Generator for After Sales Dashboard

This module includes a sample data generator to populate the dashboards with realistic data for demonstration purposes.

## How to Generate Sample Data

### Method 1: Using the Wizard (Recommended)

1. Go to **Sales → Sales Orders**
2. You'll see an action button "Generate Sample Data" in the top menu
3. Click it to open the wizard
4. Click "Generate Sample Data" button
5. The system will generate sample data and show a confirmation message

### Method 2: Using Odoo Shell

1. Open Odoo shell:
   ```bash
   python odoo-bin shell -d your_database
   ```

2. Run the generator:
   ```python
   env = self.env
   wizard = env['sample.data.generator'].create({})
   wizard.generate_sample_data()
   ```

### Method 3: Using the Demo Script

Run the demo script from Odoo shell:
```python
exec(open('after_sales_dashboard/demo/generate_sample_data.py').read())
generate_sample_data(env)
```

## What Gets Generated

The sample data generator creates:

1. **Product Categories:**
   - Cars
   - Parts & Spares
   - Services
   - Warranty

2. **Products:**
   - 5 Cars (Toyota Camry, Honda Accord, BMW 3 Series, Mercedes C-Class, Audi A4)
   - 8 Parts (Oil Filter, Brake Pads, Air Filter, Spark Plugs, Battery, Tires, Wiper, Bulb)
   - 6 Services (Maintenance, Full Service, Engine Repair, Transmission Service, AC Service, Body Repair)
   - 1 Warranty (Extended Warranty 3 Years)

3. **Customers:**
   - 10 Sample Customers

4. **Payment Terms:**
   - "30% Down, 7 Monthly Installments" (for collection forecast demo)

5. **Sale Orders:**
   - 15 Car Sales Orders (with installment payment terms)
   - 20 Service Orders (Parts, Services, Warranty, Mixed)

6. **Invoices:**
   - Automatically created for confirmed orders

## Notes

- The generator will reuse existing records if they have the same names (no duplicates)
- Orders are randomly distributed over the last 6 months (car sales) and 4 months (service orders)
- 70% of car sales use installment payment terms
- 70-80% of orders are confirmed
- 60-70% of confirmed orders have invoices created

## Using the Sample Data

After generating the sample data, you can:

1. View the **After Sales Dashboard** to see:
   - Service orders statistics
   - Service revenue trends
   - Parts sales by category
   - Service type breakdown
   - Collection forecast (installment payments)

2. View the **Sales Dashboard** to see:
   - Car sales statistics
   - Customer performance
   - Sales trends

3. Test the **Collection Forecast** feature:
   - Shows expected collections for the next 6-24 months
   - Based on payment terms (30% down, 7 monthly installments)
   - Groups collections by month

## Troubleshooting

If you encounter errors:

1. Make sure you have the required modules installed:
   - `sale`
   - `sale_management`
   - `account`
   - `stock`

2. Check Odoo logs for detailed error messages

3. Make sure you have proper access rights to create:
   - Products
   - Customers
   - Sale Orders
   - Invoices

4. If payment terms creation fails, check account module configuration

