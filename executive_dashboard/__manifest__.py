# -*- coding: utf-8 -*-
################################################################################
#
#    Executive Dashboard Module
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
    "name": "Executive Dashboard",
    "version": "17.0.1.0.0",
    "category": "Business Intelligence",
    "summary": """Executive Dashboard - Overall Company Performance""",
    "description": """The Executive dashboard module provides a comprehensive overview of company performance. 
     It includes key metrics from HR, Inventory, Sales, Purchase, Finance, and Fleet modules. 
     This dashboard gives executives a complete view of the company's overall performance at a glance.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["hr", "hr_contract", "stock", "product", "sale", "sale_management", "purchase", "account", "fleet"],
    "data": [
        "views/executive_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "executive_dashboard/static/src/css/executive_dashboard.css",
            "executive_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "executive_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "executive_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "executive_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "executive_dashboard/static/src/components/executive_dashboard_main.js",
            "executive_dashboard/static/src/components/executive_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}

