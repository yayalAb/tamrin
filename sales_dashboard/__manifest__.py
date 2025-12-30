# -*- coding: utf-8 -*-
################################################################################
#
#    Sales Dashboard Module
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
    "name": "Sales Dashboard",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "summary": """Sales Performance Dashboard with Charts and Metrics""",
    "description": """The Sales dashboard module provides a comprehensive dashboard for sales management. 
     It includes sales summary cards, customer performance tracking, sales order statistics, 
     revenue analysis, sales trends charts, customer comparison charts, and category sales charts.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["sale", "sale_management", "account"],
    "data": [
        "views/sales_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "sales_dashboard/static/src/css/sales_dashboard.css",
            "sales_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "sales_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "sales_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "sales_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "sales_dashboard/static/src/components/sales_dashboard_main.js",
            "sales_dashboard/static/src/components/sales_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}

