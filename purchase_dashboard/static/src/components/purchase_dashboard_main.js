/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class PurchaseDashboard extends Component {
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
            pending_orders: { value: 0 },
            approved_orders: { value: 0 },
            avg_order_value: { value: 0, currency: '' },
            total_vendors: { value: 0 },
            trends_chart: {
                labels: [],
                datasets: [],
            },
            vendor_chart: {
                labels: [],
                datasets: [],
            },
            category_chart: {
                labels: [],
                datasets: [],
            },
            purchase_type_chart: {
                labels: [],
                datasets: [],
            },
            urgent_purchases: { value: 0, amount: 0, currency: '' },
            sensitive_purchases: { value: 0, amount: 0, currency: '' },
            delay_chart: {
                labels: [],
                datasets: [],
            },
            total_delayed: { value: 0, amount: 0, currency: '' },
            eoq_data: {
                summary: { total_products_analyzed: 0, avg_eoq: 0 },
                top_products: [],
            },
        })

        this.orm = useService("orm")
        this.action = useService("action")

        onWillStart(async () => {
            await this.refreshData()
        })

        // Card click handlers
        this.onTotalOrdersClick = () => {
            const domain = [['state', 'in', ['purchase', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalAmountClick = () => {
            const domain = [['state', 'in', ['purchase', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onPendingOrdersClick = () => {
            const domain = [['state', '=', 'draft']]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Pending Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onApprovedOrdersClick = () => {
            const domain = [['state', '=', 'purchase']]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Approved Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalVendorsClick = () => {
            // Get unique vendors from purchase orders in date range
            const domain = [['state', 'in', ['purchase', 'done']]]
            if (this.state.start_date) {
                domain.push(['date_order', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['date_order', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Vendors",
                res_model: "res.partner",
                views: [[false, "list"], [false, "form"]],
                domain: [['supplier_rank', '>', 0]],
                target: "current",
            })
        }

        this.onUrgentPurchasesClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: [['state', 'in', ['purchase', 'done', 'draft']]],
                target: "current",
            })
        }

        this.onSensitivePurchasesClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: [['state', 'in', ['purchase', 'done', 'draft']]],
                target: "current",
            })
        }

        this.onDelayedPurchasesClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Purchase Orders",
                res_model: "purchase.order",
                views: [[false, "list"], [false, "form"]],
                domain: [['state', 'in', ['purchase', 'done']]],
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

        this.getUrgentPurchasesFormatted = () => {
            const currency = this.state.urgent_purchases.currency || ''
            const amount = this.formatCurrency(this.state.urgent_purchases.amount || 0)
            return `${currency} ${amount}`
        }

        this.getSensitivePurchasesFormatted = () => {
            const currency = this.state.sensitive_purchases.currency || ''
            const amount = this.formatCurrency(this.state.sensitive_purchases.amount || 0)
            return `${currency} ${amount}`
        }

        this.getDelayedPurchasesFormatted = () => {
            const currency = this.state.total_delayed.currency || ''
            const amount = this.formatCurrency(this.state.total_delayed.amount || 0)
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
            this.getPurchaseStatistics(),
            this.getMonthlyTrends(),
            this.getVendorPerformance(),
            this.getCategorySpending(),
            this.getPurchaseByType(),
            this.getUrgentPurchases(),
            this.getSensitivePurchases(),
            this.getDelayPeriodData(),
            this.getEconomicOrderQuantity(),
        ])
    }

    async getPurchaseStatistics() {
        try {
            const stats = await this.orm.call(
                "purchase.order",
                "get_purchase_statistics",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            this.state.total_orders.value = stats.total_orders || 0
            this.state.total_amount.value = stats.total_amount || 0.0
            this.state.pending_orders.value = stats.pending_orders || 0
            this.state.approved_orders.value = stats.approved_orders || 0
            this.state.avg_order_value.value = stats.avg_order_value || 0.0
            this.state.total_vendors.value = stats.total_vendors || 0
            
            // Get currency symbol from stats
            this.state.total_amount.currency = stats.currency_symbol || ''
            this.state.avg_order_value.currency = stats.currency_symbol || ''
        } catch (error) {
            console.error("Error loading purchase statistics:", error)
        }
    }

    async getMonthlyTrends() {
        try {
            const chartData = await this.orm.call(
                "purchase.order",
                "get_monthly_purchase_trends",
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

    async getVendorPerformance() {
        try {
            const chartData = await this.orm.call(
                "purchase.order",
                "get_vendor_performance",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.vendor_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading vendor performance:", error)
        }
    }

    async getCategorySpending() {
        try {
            const chartData = await this.orm.call(
                "purchase.order",
                "get_category_spending",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.category_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading category spending:", error)
        }
    }

    async getPurchaseByType() {
        try {
            const typeData = await this.orm.call(
                "purchase.order",
                "get_purchase_by_type",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (typeData && typeData.labels && typeData.datasets) {
                this.state.purchase_type_chart = {
                    labels: typeData.labels || [],
                    datasets: typeData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading purchase by type:", error)
        }
    }

    async getUrgentPurchases() {
        try {
            const urgentData = await this.orm.call(
                "purchase.order",
                "get_urgent_purchases",
                [this.state.start_date || null, this.state.end_date || null]
            )
            this.state.urgent_purchases.value = urgentData.count || 0
            this.state.urgent_purchases.amount = urgentData.amount || 0.0
            this.state.urgent_purchases.currency = this.state.total_amount.currency || ''
        } catch (error) {
            console.error("Error loading urgent purchases:", error)
            this.state.urgent_purchases.value = 0
            this.state.urgent_purchases.amount = 0.0
        }
    }

    async getSensitivePurchases() {
        try {
            const sensitiveData = await this.orm.call(
                "purchase.order",
                "get_sensitive_data_purchases",
                [this.state.start_date || null, this.state.end_date || null]
            )
            this.state.sensitive_purchases.value = sensitiveData.count || 0
            this.state.sensitive_purchases.amount = sensitiveData.amount || 0.0
            this.state.sensitive_purchases.currency = this.state.total_amount.currency || ''
        } catch (error) {
            console.error("Error loading sensitive purchases:", error)
            this.state.sensitive_purchases.value = 0
            this.state.sensitive_purchases.amount = 0.0
        }
    }

    async getDelayPeriodData() {
        try {
            const delayData = await this.orm.call(
                "purchase.order",
                "get_delay_period_data",
                [this.state.start_date || null, this.state.end_date || null]
            )
            this.state.total_delayed.value = delayData.total_delayed || 0
            this.state.total_delayed.amount = delayData.total_delay_amount || 0.0
            this.state.total_delayed.currency = this.state.total_amount.currency || ''
            
            if (delayData && delayData.labels && delayData.datasets) {
                this.state.delay_chart = {
                    labels: delayData.labels || [],
                    datasets: delayData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading delay period data:", error)
            this.state.total_delayed.value = 0
            this.state.total_delayed.amount = 0.0
        }
    }

    async getEconomicOrderQuantity() {
        try {
            const eoqData = await this.orm.call(
                "purchase.order",
                "get_economic_order_quantity",
                [this.state.start_date || null, this.state.end_date || null]
            )
            if (eoqData && eoqData.summary && eoqData.top_products) {
                this.state.eoq_data = {
                    summary: eoqData.summary || { total_products_analyzed: 0, avg_eoq: 0 },
                    top_products: eoqData.top_products || [],
                }
            }
        } catch (error) {
            console.error("Error loading economic order quantity:", error)
        }
    }
}

PurchaseDashboard.template = "purchase_dashboard.PurchaseDashboard"
PurchaseDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("purchase_dashboard.purchase_dashboard", PurchaseDashboard)

