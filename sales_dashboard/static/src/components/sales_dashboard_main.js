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
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: lastDayOfMonth.toISOString().split('T')[0],
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
            console.log("Fetching sales statistics with dates:", this.state.start_date, this.state.end_date)
            const stats = await this.orm.call(
                "sale.order",
                "get_sales_statistics",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            console.log("Sales statistics received:", stats)
            
            if (stats) {
                this.state.total_orders.value = stats.total_orders || 0
                this.state.total_amount.value = stats.total_amount || 0.0
                this.state.quotation_orders.value = stats.quotation_orders || 0
                this.state.confirmed_orders.value = stats.confirmed_orders || 0
                this.state.avg_order_value.value = stats.avg_order_value || 0.0
                this.state.total_customers.value = stats.total_customers || 0
                
                // Get currency symbol from stats
                this.state.total_amount.currency = stats.currency_symbol || ''
                this.state.avg_order_value.currency = stats.currency_symbol || ''
                
                console.log("Sales statistics updated:", {
                    total_orders: this.state.total_orders.value,
                    total_amount: this.state.total_amount.value,
                    quotation_orders: this.state.quotation_orders.value,
                    confirmed_orders: this.state.confirmed_orders.value,
                    avg_order_value: this.state.avg_order_value.value,
                    total_customers: this.state.total_customers.value,
                })
            } else {
                console.warn("No sales statistics data received")
            }
        } catch (error) {
            console.error("Error loading sales statistics:", error)
            console.error("Error details:", error.message, error.stack)
        }
    }

    async getMonthlyTrends() {
        try {
            console.log("Fetching monthly trends with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_monthly_sales_trends",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Monthly trends data received:", chartData)
            
            // Log the actual data values
            if (chartData && chartData.datasets) {
                chartData.datasets.forEach((dataset, index) => {
                    console.log(`Dataset ${index} (${dataset.label}):`, dataset.data)
                    console.log(`  - First 3 values:`, dataset.data.slice(0, 3))
                    console.log(`  - Last 3 values:`, dataset.data.slice(-3))
                    console.log(`  - Sum of all values:`, dataset.data.reduce((a, b) => a + b, 0))
                })
            }

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.trends_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Monthly trends chart updated - labels:", this.state.trends_chart.labels.length, 
                           "datasets:", this.state.trends_chart.datasets.length)
                console.log("Chart labels:", this.state.trends_chart.labels)
            } else {
                console.warn("Invalid monthly trends data:", chartData)
                this.state.trends_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading monthly trends:", error)
            console.error("Error details:", error.message, error.stack)
            this.state.trends_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getCustomerPerformance() {
        try {
            console.log("Fetching customer performance with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_customer_performance",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Customer performance data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.customer_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Customer performance chart updated - labels:", this.state.customer_chart.labels.length, 
                           "datasets:", this.state.customer_chart.datasets.length)
            } else {
                console.warn("Invalid customer performance data:", chartData)
                this.state.customer_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading customer performance:", error)
            console.error("Error details:", error.message, error.stack)
            this.state.customer_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getCategorySales() {
        try {
            console.log("Fetching category sales with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_category_sales",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Category sales data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.category_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Category sales chart updated - labels:", this.state.category_chart.labels.length, 
                           "datasets:", this.state.category_chart.datasets.length)
            } else {
                console.warn("Invalid category sales data:", chartData)
                this.state.category_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading category sales:", error)
            console.error("Error details:", error.message, error.stack)
            this.state.category_chart = {
                labels: [],
                datasets: [],
            }
        }
    }
}

SalesDashboard.template = "sales_dashboard.SalesDashboard"
SalesDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("sales_dashboard.sales_dashboard", SalesDashboard)

