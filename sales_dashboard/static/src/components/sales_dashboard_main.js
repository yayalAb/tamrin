/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class SalesDashboard extends Component {
    setup() {
        // Set default dates to current month
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: today.toISOString().split('T')[0],
            total_orders: { value: 0 },
            total_amount: { value: 0, currency: '' },
            quotation_orders: { value: 0 },
            confirmed_orders: { value: 0 },
            avg_order_value: { value: 0, currency: '' },
            total_customers: { value: 0 },
            trends_chart: {
                labels: [],
                datasets: [],
            },
            customer_chart: {
                labels: [],
                datasets: [],
            },
            category_chart: {
                labels: [],
                datasets: [],
            },
        })

        this.orm = useService("orm")
        this.action = useService("action")

        onWillStart(async () => {
            await this.refreshData()
        })

        // Card click handlers
        this.onTotalOrdersClick = () => {
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Sales Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalAmountClick = () => {
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Sales Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onQuotationOrdersClick = () => {
            const domain = [['state', '=', 'draft']]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Quotations",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onConfirmedOrdersClick = () => {
            const domain = [['state', '=', 'sale']]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Confirmed Sales Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalCustomersClick = () => {
            // Get unique customers from sales orders in date range
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Customers",
                res_model: "res.partner",
                views: [[false, "list"], [false, "form"]],
                domain: [['customer_rank', '>', 0]],
                target: "current",
            })
        }

        this.formatCurrency = (amount) => {
            if (!amount && amount !== 0) return "0.00"
            return amount.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })
        }

        // Computed properties for formatted values
        this.getTotalAmountFormatted = () => {
            const currency = this.state.total_amount.currency || ''
            const amount = this.formatCurrency(this.state.total_amount.value || 0)
            return `${currency} ${amount}`
        }

        this.getAvgOrderValueFormatted = () => {
            const currency = this.state.avg_order_value.currency || ''
            const amount = this.formatCurrency(this.state.avg_order_value.value || 0)
            return `${currency} ${amount}`
        }

        this.onStartDateChange = async ev => {
            this.state.start_date = ev.target.value
            await this.refreshData()
        }

        this.onEndDateChange = async ev => {
            this.state.end_date = ev.target.value
            await this.refreshData()
        }
    }

    async refreshData() {
        await Promise.all([
            this.getSalesStatistics(),
            this.getMonthlyTrends(),
            this.getCustomerPerformance(),
            this.getCategorySales(),
        ])
    }

    async getSalesStatistics() {
        try {
            const stats = await this.orm.call(
                "sale.order",
                "get_sales_statistics",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            this.state.total_orders.value = stats.total_orders || 0
            this.state.total_amount.value = stats.total_amount || 0.0
            this.state.quotation_orders.value = stats.quotation_orders || 0
            this.state.confirmed_orders.value = stats.confirmed_orders || 0
            this.state.avg_order_value.value = stats.avg_order_value || 0.0
            this.state.total_customers.value = stats.total_customers || 0
            
            // Get currency symbol from stats
            this.state.total_amount.currency = stats.currency_symbol || ''
            this.state.avg_order_value.currency = stats.currency_symbol || ''
        } catch (error) {
            console.error("Error loading sales statistics:", error)
        }
    }

    async getMonthlyTrends() {
        try {
            const chartData = await this.orm.call(
                "sale.order",
                "get_monthly_sales_trends",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.trends_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading monthly trends:", error)
        }
    }

    async getCustomerPerformance() {
        try {
            const chartData = await this.orm.call(
                "sale.order",
                "get_customer_performance",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.customer_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading customer performance:", error)
        }
    }

    async getCategorySales() {
        try {
            const chartData = await this.orm.call(
                "sale.order",
                "get_category_sales",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.category_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading category sales:", error)
        }
    }
}

SalesDashboard.template = "sales_dashboard.SalesDashboard"
SalesDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("sales_dashboard.sales_dashboard", SalesDashboard)

