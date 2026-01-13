# -*- coding: utf-8 -*-
################################################################################
#
#    After Sales Dashboard Module - Car Sales Industry
#
#    Copyright (C) 2024-TODAY Your Company.
#    Author: Your Name
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
{
    "name": "After Sales Dashboard - Car Sales Industry",
    "version": "17.0.1.0.0",
    "category": "Sales/After Sales",
    "summary": """After Sales Report Dashboard for Car Sales Industry with Service Orders, Repairs, Parts Sales, and Warranty Tracking""",
    "description": """The After Sales Dashboard module provides a comprehensive dashboard for after-sales services in the car sales industry. 
     It includes service order tracking, repair order management, parts sales analysis, warranty claims monitoring,
     service revenue tracking, customer service metrics, technician performance, and service type breakdown.
     Features include monthly service trends, parts sales by category, warranty claims status, and customer retention metrics.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["sale", "sale_management", "account", "stock"],
    "data": [
        "views/after_sales_dashboard_menu.xml",
        "wizard/sample_data_wizard.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "after_sales_dashboard/static/src/css/after_sales_dashboard.css",
            "after_sales_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "after_sales_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "after_sales_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "after_sales_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "after_sales_dashboard/static/src/components/after_sales_dashboard_main.js",
            "after_sales_dashboard/static/src/components/after_sales_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}

