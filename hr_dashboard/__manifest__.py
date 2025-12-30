# -*- coding: utf-8 -*-
################################################################################
#
#    HR Dashboard Module
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
    "name": "HR Dashboard",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "summary": """HR Dashboard with Charts and Metrics""",
    "description": """The HR dashboard module provides a comprehensive dashboard for HR management. 
     It includes employee summary cards, contract tracking, leave requests monitoring, 
     appraisals tracking, recruitment metrics, resignation tracking, employee inventory charts, 
     monthly payroll charts, and department headcount charts.""",
    "author": "Your Company",
    "company": "Your Company",
    "maintainer": "Your Company",
    "website": "https://www.yourcompany.com",
    "depends": ["hr", "hr_contract"],
    "data": [
        "views/hr_dashboard_menu.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "hr_dashboard/static/src/css/hr_dashboard.css",
            "hr_dashboard/static/src/components/chart_renderer/chart_renderer.js",
            "hr_dashboard/static/src/components/chart_renderer/chart_renderer.xml",
            "hr_dashboard/static/src/components/dashboard_card/dashboard_card.js",
            "hr_dashboard/static/src/components/dashboard_card/dashboard_card.xml",
            "hr_dashboard/static/src/components/hr_dashboard_main.js",
            "hr_dashboard/static/src/components/hr_dashboard_main.xml",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}
