# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseReportSummary(models.Model):
    _name = "purchase.report.summary"
    _description = "Purchase Report Summary"
    _auto = False
    _order = "purchase_date desc, part_number"

    sequence = fields.Integer(string="SN.", readonly=True)
    part_number = fields.Char(string="Part Number (ID)", readonly=True)
    description = fields.Text(string="Description", readonly=True)
    uom = fields.Char(string="UOM", readonly=True)
    purchased_qty = fields.Float(string="Purchased Qty", readonly=True, digits="Product Unit of Measure")
    purchase_date = fields.Date(string="Purchased Date", readonly=True)
    unit_price = fields.Float(string="Unit Price", readonly=True, digits="Product Unit of Measure")
    unit_cost = fields.Float(string="Unit Cost", readonly=True, digits="Product Unit of Measure")
    order_id = fields.Many2one("purchase.order", string="Purchase Order", readonly=True)
    product_id = fields.Many2one("product.product", string="Product", readonly=True)

    def init(self):
        # Extract JSONB name fields with language fallback
        # Group by product_id ONLY to ensure each product appears exactly once
        # Try common languages: en_US, en, ar, fr_FR, then first available
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW purchase_report_summary AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY pol.product_id) AS id,
                    ROW_NUMBER() OVER (ORDER BY pol.product_id) AS sequence,
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
                    SUM(COALESCE(pol.product_qty, 0.0)) AS purchased_qty,
                    MAX(DATE(po.date_order)) AS purchase_date,
                    AVG(COALESCE(pol.price_unit, 0.0)) AS unit_price,
                    AVG(COALESCE(pol.price_unit, 0.0)) AS unit_cost,
                    MIN(po.id) AS order_id,
                    pol.product_id AS product_id
                FROM purchase_order_line pol
                INNER JOIN purchase_order po ON pol.order_id = po.id
                LEFT JOIN product_product pp ON pol.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN uom_uom uom ON pol.product_uom = uom.id
                WHERE po.state IN ('purchase', 'done')
                    AND pol.product_id IS NOT NULL
                GROUP BY pol.product_id
            )
        """)

