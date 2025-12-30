# -*- coding: utf-8 -*-
################################################################################
#
#    Inventory Dashboard Module
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
    "name": "Inventory Dashboard",
    "version": "17.0.1.0.0",
    "category": "Inventory",
    "summary": """Inventory Performance Dashboard with Charts and Metrics""",
    "description": """The Inventory dashboard module provides a comprehensive dashboard for inventory management. 
     It includes inventory summary cards, stock level tracking, low stock alerts, 
     stock value analysis, inventory trends charts, category stock charts, and location performance charts.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["stock", "product"],
    "data": [
        "views/inventory_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "inventory_dashboard/static/src/css/inventory_dashboard.css",
            "inventory_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "inventory_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "inventory_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "inventory_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "inventory_dashboard/static/src/components/inventory_dashboard_main.js",
            "inventory_dashboard/static/src/components/inventory_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}

