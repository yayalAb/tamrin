# -*- coding: utf-8 -*-

from odoo import fields, models


class InventoryReportSummary(models.Model):
    _name = "inventory.report.summary"
    _description = "Inventory Report Summary"
    _auto = False
    _order = "part_number"

    sequence = fields.Integer(string="SN.", readonly=True)
    part_number = fields.Char(string="Part Number (ID)", readonly=True)
    description = fields.Text(string="Description", readonly=True)
    uom = fields.Char(string="UOM", readonly=True)
    all_received_qty = fields.Float(string="All Received Qty", readonly=True, digits="Product Unit of Measure")
    date_of_receipt = fields.Date(string="Date of Receipt", readonly=True)
    sold_qty = fields.Float(string="Sold Qty", readonly=True, digits="Product Unit of Measure")
    sold_date = fields.Date(string="Sold Date", readonly=True)
    remaining_qty = fields.Float(string="Remaining Qty", readonly=True, digits="Product Unit of Measure")
    unit_price = fields.Float(string="Unit Price", readonly=True, digits="Product Unit of Measure")
    unit_cost = fields.Float(string="Unit Cost", readonly=True, digits="Product Unit of Measure")
    abc_group = fields.Char(string="ABC GROUP", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)

    def init(self):
        # Extract JSONB name fields with language fallback
        # Combine purchase, sales, and stock data
        # Group by product_id to ensure each product appears once
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW inventory_report_summary AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY COALESCE(pp.id, 0)) AS id,
                    ROW_NUMBER() OVER (ORDER BY COALESCE(pp.id, 0)) AS sequence,
                    MAX(COALESCE(pp.default_code::text, '')) AS part_number,
                    MAX(COALESCE(
                        CASE 
                            WHEN pt.name IS NULL THEN ''
                            WHEN jsonb_typeof(pt.name) = 'object' THEN 
                                COALESCE(
                                    pt.name->>'en_US',
                                    pt.name->>'en',
                                    pt.name->>'ar',
                                    pt.name->>'fr_FR',
                                    (SELECT value FROM jsonb_each_text(pt.name) LIMIT 1)
                                )
                            ELSE pt.name::text
                        END,
                        ''
                    )) AS description,
                    MAX(COALESCE(
                        CASE 
                            WHEN uom.name IS NULL THEN ''
                            WHEN jsonb_typeof(uom.name) = 'object' THEN 
                                COALESCE(
                                    uom.name->>'en_US',
                                    uom.name->>'en',
                                    uom.name->>'ar',
                                    uom.name->>'fr_FR',
                                    (SELECT value FROM jsonb_each_text(uom.name) LIMIT 1)
                                )
                            ELSE uom.name::text
                        END,
                        ''
                    )) AS uom,
                    COALESCE(SUM(purchase_data.purchased_qty), 0.0) AS all_received_qty,
                    MAX(purchase_data.purchase_date) AS date_of_receipt,
                    COALESCE(SUM(sales_data.sold_qty), 0.0) AS sold_qty,
                    MAX(sales_data.sale_date) AS sold_date,
                    COALESCE(MAX(stock_data.qty_available), 0.0) AS remaining_qty,
                    AVG(COALESCE(price_data.unit_price, 0.0)) AS unit_price,
                    AVG(COALESCE(price_data.unit_cost, 0.0)) AS unit_cost,
                    '' AS abc_group,
                    COALESCE(pp.id, purchase_data.product_id, sales_data.product_id) AS product_id
                FROM product_product pp
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN uom_uom uom ON pt.uom_id = uom.id
                LEFT JOIN (
                    SELECT 
                        pol.product_id,
                        SUM(COALESCE(pol.product_qty, 0.0)) AS purchased_qty,
                        MAX(DATE(po.date_order)) AS purchase_date
                    FROM purchase_order_line pol
                    INNER JOIN purchase_order po ON pol.order_id = po.id
                    WHERE po.state IN ('purchase', 'done')
                        AND pol.product_id IS NOT NULL
                    GROUP BY pol.product_id
                ) purchase_data ON pp.id = purchase_data.product_id
                LEFT JOIN (
                    SELECT 
                        sol.product_id,
                        SUM(COALESCE(sol.product_uom_qty, 0.0)) AS sold_qty,
                        MAX(DATE(so.date_order)) AS sale_date
                    FROM sale_order_line sol
                    INNER JOIN sale_order so ON sol.order_id = so.id
                    WHERE so.state IN ('sale', 'done')
                        AND sol.product_id IS NOT NULL
                    GROUP BY sol.product_id
                ) sales_data ON pp.id = sales_data.product_id
                LEFT JOIN (
                    SELECT 
                        product_id,
                        SUM(quantity) AS qty_available
                    FROM stock_quant
                    WHERE location_id IN (
                        SELECT id FROM stock_location 
                        WHERE usage = 'internal'
                    )
                    GROUP BY product_id
                ) stock_data ON pp.id = stock_data.product_id
                LEFT JOIN (
                    SELECT 
                        product_id,
                        AVG(price_unit) AS unit_price,
                        AVG(price_unit) AS unit_cost
                    FROM (
                        SELECT product_id, price_unit 
                        FROM sale_order_line 
                        WHERE order_id IN (
                            SELECT id FROM sale_order WHERE state IN ('sale', 'done')
                        )
                        UNION ALL
                        SELECT product_id, price_unit 
                        FROM purchase_order_line 
                        WHERE order_id IN (
                            SELECT id FROM purchase_order WHERE state IN ('purchase', 'done')
                        )
                    ) price_union
                    GROUP BY product_id
                ) price_data ON pp.id = price_data.product_id
                WHERE pp.id IS NOT NULL
                    AND (
                        purchase_data.product_id IS NOT NULL 
                        OR sales_data.product_id IS NOT NULL 
                        OR stock_data.product_id IS NOT NULL
                    )
                GROUP BY pp.id, purchase_data.product_id, sales_data.product_id
            )
        """)

