/** @odoo-module */

const { Component } = owl
export class DashboardCard extends Component {
    static template = "finance_dashboard.DashboardCard"
    static props = {
        name: String,
        value: [Number, String],
        iconClass: String,
        bgColor: String,
        onClick: { type: Function, optional: true },
    }
}

