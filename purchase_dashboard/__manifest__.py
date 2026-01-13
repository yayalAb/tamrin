# -*- coding: utf-8 -*-
################################################################################
#
#    Purchase Dashboard Module
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
    "name": "Purchase Dashboard",
    "version": "17.0.1.0.0",
    "category": "Purchases",
    "summary": """Purchase Performance Dashboard with Charts and Metrics""",
    "description": """The Purchase dashboard module provides a comprehensive dashboard for purchase management. 
     It includes purchase summary cards, vendor performance tracking, purchase order statistics, 
     spending analysis, purchase trends charts, vendor comparison charts, and category spending charts.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["purchase", "account"],
    "data": [
        "views/purchase_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "purchase_dashboard/static/src/css/purchase_dashboard.css",
            "purchase_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "purchase_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "purchase_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "purchase_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "purchase_dashboard/static/src/components/purchase_dashboard_main.js",
            "purchase_dashboard/static/src/components/purchase_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}


