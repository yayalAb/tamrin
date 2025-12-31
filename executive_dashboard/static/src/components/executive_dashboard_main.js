/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class ExecutiveDashboard extends Component {
    setup() {
        // Set default dates to current month
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: lastDayOfMonth.toISOString().split('T')[0],
            // HR Metrics
            total_employees: { value: 0 },
            expiring_contracts: { value: 0 },
            total_payroll: { value: 0, currency: '' },
            // Inventory Metrics
            total_products: { value: 0 },
            low_stock_products: { value: 0 },
            total_stock_value: { value: 0, currency: '' },
            // Sales Metrics
            total_sales_orders: { value: 0 },
            total_sales_revenue: { value: 0, currency: '' },
            quotations: { value: 0 },
            // Purchase Metrics
            total_purchase_orders: { value: 0 },
            total_purchase_amount: { value: 0, currency: '' },
            pending_purchases: { value: 0 },
            // Finance Metrics
            total_revenue: { value: 0, currency: '' },
            net_revenue: { value: 0, currency: '' },
            total_expenses: { value: 0, currency: '' },
            profit: { value: 0, currency: '' },
            // Fleet Metrics
            total_vehicles: { value: 0 },
            active_vehicles: { value: 0 },
            // Charts
            revenue_expenses_chart: {
                labels: [],
                datasets: [],
            },
            sales_purchase_chart: {
                labels: [],
                datasets: [],
            },
            department_chart: {
                labels: [],
                datasets: [],
            },
        })

        this.orm = useService("orm")
        this.action = useService("action")

        onWillStart(async () => {
            await this.refreshData()
        })

        this.formatCurrency = (amount) => {
            if (!amount && amount !== 0) return "0.00"
            return amount.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })
        }

        // Computed properties for formatted values
        this.getTotalPayrollFormatted = () => {
            const currency = this.state.total_payroll.currency || ''
            const amount = this.formatCurrency(this.state.total_payroll.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalStockValueFormatted = () => {
            const currency = this.state.total_stock_value.currency || ''
            const amount = this.formatCurrency(this.state.total_stock_value.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalSalesRevenueFormatted = () => {
            const currency = this.state.total_sales_revenue.currency || ''
            const amount = this.formatCurrency(this.state.total_sales_revenue.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalPurchaseAmountFormatted = () => {
            const currency = this.state.total_purchase_amount.currency || ''
            const amount = this.formatCurrency(this.state.total_purchase_amount.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalRevenueFormatted = () => {
            const currency = this.state.total_revenue.currency || ''
            const amount = this.formatCurrency(this.state.total_revenue.value || 0)
            return `${currency} ${amount}`
        }

        this.getNetRevenueFormatted = () => {
            const currency = this.state.net_revenue.currency || ''
            const amount = this.formatCurrency(this.state.net_revenue.value || 0)
            return `${currency} ${amount}`
        }

        this.getTotalExpensesFormatted = () => {
            const currency = this.state.total_expenses.currency || ''
            const amount = this.formatCurrency(this.state.total_expenses.value || 0)
            return `${currency} ${amount}`
        }

        this.getProfitFormatted = () => {
            const currency = this.state.profit.currency || ''
            const amount = this.formatCurrency(this.state.profit.value || 0)
            return `${currency} ${amount}`
        }

        this.getHREmployeesFormatted = () => {
            return `${this.state.total_employees.value || 0} Employees`
        }

        this.getFleetActiveFormatted = () => {
            return `${this.state.active_vehicles.value || 0} Active`
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
            this.getCompanyOverview(),
            this.getRevenueVsExpenses(),
            this.getSalesVsPurchase(),
            this.getDepartmentPerformance(),
        ])
    }

    async getCompanyOverview() {
        try {
            const overview = await this.orm.call(
                "executive.dashboard",
                "get_company_overview",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            // HR
            this.state.total_employees.value = overview.total_employees || 0
            this.state.expiring_contracts.value = overview.expiring_contracts || 0
            this.state.total_payroll.value = overview.total_payroll || 0.0
            this.state.total_payroll.currency = overview.currency_symbol || ''
            
            // Inventory
            this.state.total_products.value = overview.total_products || 0
            this.state.low_stock_products.value = overview.low_stock_products || 0
            this.state.total_stock_value.value = overview.total_stock_value || 0.0
            this.state.total_stock_value.currency = overview.currency_symbol || ''
            
            // Sales
            this.state.total_sales_orders.value = overview.total_sales_orders || 0
            this.state.total_sales_revenue.value = overview.total_sales_revenue || 0.0
            this.state.total_sales_revenue.currency = overview.currency_symbol || ''
            this.state.quotations.value = overview.quotations || 0
            
            // Purchase
            this.state.total_purchase_orders.value = overview.total_purchase_orders || 0
            this.state.total_purchase_amount.value = overview.total_purchase_amount || 0.0
            this.state.total_purchase_amount.currency = overview.currency_symbol || ''
            this.state.pending_purchases.value = overview.pending_purchases || 0
            
            // Finance
            this.state.total_revenue.value = overview.total_revenue || 0.0
            this.state.total_revenue.currency = overview.currency_symbol || ''
            this.state.net_revenue.value = overview.net_revenue || 0.0
            this.state.net_revenue.currency = overview.currency_symbol || ''
            this.state.total_expenses.value = overview.total_expenses || 0.0
            this.state.total_expenses.currency = overview.currency_symbol || ''
            this.state.profit.value = overview.profit || 0.0
            this.state.profit.currency = overview.currency_symbol || ''
            
            // Fleet
            this.state.total_vehicles.value = overview.total_vehicles || 0
            this.state.active_vehicles.value = overview.active_vehicles || 0
        } catch (error) {
            console.error("Error loading company overview:", error)
        }
    }

    async getRevenueVsExpenses() {
        try {
            const chartData = await this.orm.call(
                "executive.dashboard",
                "get_revenue_vs_expenses",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.revenue_expenses_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading revenue vs expenses:", error)
        }
    }

    async getSalesVsPurchase() {
        try {
            const chartData = await this.orm.call(
                "executive.dashboard",
                "get_sales_vs_purchase",
                [this.state.start_date || null, this.state.end_date || null]
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.sales_purchase_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading sales vs purchase:", error)
        }
    }

    async getDepartmentPerformance() {
        try {
            const chartData = await this.orm.call(
                "executive.dashboard",
                "get_department_performance",
                []
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.department_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading department performance:", error)
        }
    }
}

ExecutiveDashboard.template = "executive_dashboard.ExecutiveDashboard"
ExecutiveDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("executive_dashboard.executive_dashboard", ExecutiveDashboard)

