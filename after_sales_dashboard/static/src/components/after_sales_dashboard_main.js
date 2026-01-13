/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class AfterSalesDashboard extends Component {
    setup() {
        // Set default dates to current month
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: lastDayOfMonth.toISOString().split('T')[0],
            total_service_orders: { value: 0 },
            total_service_revenue: { value: 0, currency: '' },
            avg_service_value: { value: 0, currency: '' },
            total_customers: { value: 0 },
            warranty_claims: { value: 0 },
            parts_revenue: { value: 0, currency: '' },
            trends_chart: {
                labels: [],
                datasets: [],
            },
            service_type_chart: {
                labels: [],
                datasets: [],
            },
            customer_chart: {
                labels: [],
                datasets: [],
            },
            parts_category_chart: {
                labels: [],
                datasets: [],
            },
            invoice_status_chart: {
                labels: [],
                datasets: [],
            },
            collection_forecast_chart: {
                labels: [],
                datasets: [],
            },
            total_expected_collections: { value: 0, currency: '' },
            forecast_months: 12,
        })

        this.orm = useService("orm")
        this.action = useService("action")

        onWillStart(async () => {
            await this.refreshData()
        })

        // Card click handlers
        this.onTotalServiceOrdersClick = () => {
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Service Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalRevenueClick = () => {
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Service Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onPendingOrdersClick = () => {
            const domain = [['state', 'in', ['draft', 'sale']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Pending Service Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onCompletedOrdersClick = () => {
            const domain = [['state', '=', 'done']]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Completed Service Orders",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalCustomersClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Service Customers",
                res_model: "res.partner",
                views: [[false, "list"], [false, "form"]],
                domain: [['customer_rank', '>', 0]],
                target: "current",
            })
        }

        this.onWarrantyClaimsClick = () => {
            const domain = [['state', 'in', ['sale', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Warranty Claims",
                res_model: "sale.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
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
        this.getTotalRevenueFormatted = () => {
            const currency = this.state.total_service_revenue.currency || ''
            const amount = this.formatCurrency(this.state.total_service_revenue.value || 0)
            return `${currency} ${amount}`
        }

        this.getAvgServiceValueFormatted = () => {
            const currency = this.state.avg_service_value.currency || ''
            const amount = this.formatCurrency(this.state.avg_service_value.value || 0)
            return `${currency} ${amount}`
        }

        this.getPartsRevenueFormatted = () => {
            const currency = this.state.parts_revenue.currency || ''
            const amount = this.formatCurrency(this.state.parts_revenue.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalExpectedCollectionsFormatted = () => {
            const currency = this.state.total_expected_collections.currency || ''
            const amount = this.formatCurrency(this.state.total_expected_collections.value || 0)
            return `${currency} ${amount}`
        }

        this.onForecastMonthsChange = async ev => {
            this.state.forecast_months = parseInt(ev.target.value) || 12
            await this.getCollectionForecast()
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
            this.getAfterSalesStatistics(),
            this.getMonthlyTrends(),
            this.getServiceTypeBreakdown(),
            this.getCustomerPerformance(),
            this.getPartsCategorySales(),
            this.getInvoiceStatus(),
            this.getCollectionForecast(),
        ])
    }

    async getAfterSalesStatistics() {
        try {
            console.log("Fetching after-sales statistics with dates:", this.state.start_date, this.state.end_date)
            const stats = await this.orm.call(
                "sale.order",
                "get_after_sales_statistics",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            console.log("After-sales statistics received:", stats)
            
            if (stats) {
                this.state.total_service_orders.value = stats.total_service_orders || 0
                this.state.total_service_revenue.value = stats.total_service_revenue || 0.0
                this.state.avg_service_value.value = stats.avg_service_value || 0.0
                this.state.total_customers.value = stats.total_customers || 0
                this.state.warranty_claims.value = stats.warranty_claims || 0
                this.state.parts_revenue.value = stats.parts_revenue || 0.0
                
                // Get currency symbol from stats
                this.state.total_service_revenue.currency = stats.currency_symbol || ''
                this.state.avg_service_value.currency = stats.currency_symbol || ''
                this.state.parts_revenue.currency = stats.currency_symbol || ''
                
                console.log("After-sales statistics updated:", {
                    total_service_orders: this.state.total_service_orders.value,
                    total_service_revenue: this.state.total_service_revenue.value,
                    avg_service_value: this.state.avg_service_value.value,
                    total_customers: this.state.total_customers.value,
                    warranty_claims: this.state.warranty_claims.value,
                    parts_revenue: this.state.parts_revenue.value,
                })
            } else {
                console.warn("No after-sales statistics data received")
            }
        } catch (error) {
            console.error("Error loading after-sales statistics:", error)
            console.error("Error details:", error.message, error.stack)
        }
    }

    async getMonthlyTrends() {
        try {
            console.log("Fetching monthly service trends with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_monthly_service_trends",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Monthly service trends data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.trends_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Monthly trends chart updated")
            } else {
                console.warn("Invalid monthly trends data:", chartData)
                this.state.trends_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading monthly trends:", error)
            this.state.trends_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getServiceTypeBreakdown() {
        try {
            console.log("Fetching service type breakdown with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_service_type_breakdown",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Service type breakdown data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.service_type_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Service type chart updated")
            } else {
                console.warn("Invalid service type breakdown data:", chartData)
                this.state.service_type_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading service type breakdown:", error)
            this.state.service_type_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getCustomerPerformance() {
        try {
            console.log("Fetching customer service performance with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_customer_service_performance",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Customer service performance data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.customer_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Customer performance chart updated")
            } else {
                console.warn("Invalid customer performance data:", chartData)
                this.state.customer_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading customer performance:", error)
            this.state.customer_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getPartsCategorySales() {
        try {
            console.log("Fetching parts category sales with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "sale.order",
                "get_parts_category_sales",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Parts category sales data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.parts_category_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Parts category chart updated")
            } else {
                console.warn("Invalid parts category sales data:", chartData)
                this.state.parts_category_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading parts category sales:", error)
            this.state.parts_category_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getInvoiceStatus() {
        try {
            console.log("Fetching invoice status with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "account.move",
                "get_service_revenue_by_status",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Invoice status data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.invoice_status_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Invoice status chart updated")
            } else {
                console.warn("Invalid invoice status data:", chartData)
                this.state.invoice_status_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading invoice status:", error)
            this.state.invoice_status_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getCollectionForecast() {
        try {
            console.log("Fetching collection forecast with dates:", this.state.start_date, this.state.end_date, "months:", this.state.forecast_months)
            const forecastData = await this.orm.call(
                "sale.order",
                "get_collection_forecast",
                [this.state.start_date || null, this.state.end_date || null, this.state.forecast_months || 12]
            )

            console.log("Collection forecast data received:", forecastData)

            if (forecastData && forecastData.labels && forecastData.datasets) {
                this.state.collection_forecast_chart = {
                    labels: forecastData.labels || [],
                    datasets: forecastData.datasets || [],
                }
                this.state.total_expected_collections.value = forecastData.total_expected || 0.0
                this.state.total_expected_collections.currency = forecastData.currency_symbol || ''
                console.log("Collection forecast chart updated, total expected:", this.state.total_expected_collections.value)
            } else {
                console.warn("Invalid collection forecast data:", forecastData)
                this.state.collection_forecast_chart = {
                    labels: [],
                    datasets: [],
                }
                this.state.total_expected_collections.value = 0.0
                this.state.total_expected_collections.currency = ''
            }
        } catch (error) {
            console.error("Error loading collection forecast:", error)
            this.state.collection_forecast_chart = {
                labels: [],
                datasets: [],
            }
            this.state.total_expected_collections.value = 0.0
            this.state.total_expected_collections.currency = ''
        }
    }
}

AfterSalesDashboard.template = "after_sales_dashboard.AfterSalesDashboard"
AfterSalesDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("after_sales_dashboard.after_sales_dashboard", AfterSalesDashboard)

