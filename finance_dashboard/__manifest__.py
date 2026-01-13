# -*- coding: utf-8 -*-
################################################################################
#
#    Finance Dashboard Module
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
    "name": "Finance Dashboard",
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "summary": """Finance Dashboard with Key Financial Metrics and Charts""",
    "description": """The Finance dashboard module provides a comprehensive dashboard for financial management. 
     It includes revenue tracking, expense analysis, profit calculations, accounts receivable/payable, 
     cash flow monitoring, revenue vs expenses trends, profit trends, and payment status breakdown.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["account"],
    "data": [
        "views/finance_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "finance_dashboard/static/src/css/finance_dashboard.css",
            "finance_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "finance_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "finance_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "finance_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "finance_dashboard/static/src/components/finance_dashboard_main.js",
            "finance_dashboard/static/src/components/finance_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}

