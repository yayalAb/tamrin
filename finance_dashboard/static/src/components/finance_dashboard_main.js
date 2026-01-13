/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class FinanceDashboard extends Component {
    setup() {
        // Set default dates to current month
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: lastDayOfMonth.toISOString().split('T')[0],
            total_revenue: { value: 0, currency: '' },
            net_revenue: { value: 0, currency: '' },
            total_expenses: { value: 0, currency: '' },
            net_expenses: { value: 0, currency: '' },
            profit: { value: 0, currency: '' },
            accounts_receivable: { value: 0, currency: '' },
            accounts_payable: { value: 0, currency: '' },
            cash_inflow: { value: 0, currency: '' },
            cash_outflow: { value: 0, currency: '' },
            net_cash_flow: { value: 0, currency: '' },
            total_invoices: { value: 0 },
            paid_invoices_count: { value: 0 },
            unpaid_invoices_count: { value: 0 },
            total_bills: { value: 0 },
            paid_bills_count: { value: 0 },
            unpaid_bills_count: { value: 0 },
            revenue_expenses_chart: {
                labels: [],
                datasets: [],
            },
            payment_status_chart: {
                labels: [],
                datasets: [],
            },
            cash_flow_chart: {
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
        this.onTotalRevenueClick = () => {
            const domain = [
                ['move_type', 'in', ['out_invoice', 'out_refund']],
                ['state', '=', 'posted']
            ]
            if (this.state.start_date) {
                domain.push(['invoice_date', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['invoice_date', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Customer Invoices",
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalExpensesClick = () => {
            const domain = [
                ['move_type', 'in', ['in_invoice', 'in_refund']],
                ['state', '=', 'posted']
            ]
            if (this.state.start_date) {
                domain.push(['invoice_date', '>=', this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(['invoice_date', '<=', this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Vendor Bills",
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onProfitClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Financial Overview",
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain: [('state', '=', 'posted')],
                target: "current",
            })
        }

        this.onAccountsReceivableClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Accounts Receivable",
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain: [
                    ['move_type', '=', 'out_invoice'],
                    ['state', '=', 'posted'],
                    ['payment_state', 'in', ['not_paid', 'partial']]
                ],
                target: "current",
            })
        }

        this.onAccountsPayableClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Accounts Payable",
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain: [
                    ['move_type', '=', 'in_invoice'],
                    ['state', '=', 'posted'],
                    ['payment_state', 'in', ['not_paid', 'partial']]
                ],
                target: "current",
            })
        }

        this.onCashFlowClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Cash Flow",
                res_model: "account.payment",
                views: [[false, "list"], [false, "form"]],
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

        this.getAccountsReceivableFormatted = () => {
            const currency = this.state.accounts_receivable.currency || ''
            const amount = this.formatCurrency(this.state.accounts_receivable.value || 0)
            return `${currency} ${amount}`
        }

        this.getAccountsPayableFormatted = () => {
            const currency = this.state.accounts_payable.currency || ''
            const amount = this.formatCurrency(this.state.accounts_payable.value || 0)
            return `${currency} ${amount}`
        }

        this.getNetCashFlowFormatted = () => {
            const currency = this.state.net_cash_flow.currency || ''
            const amount = this.formatCurrency(this.state.net_cash_flow.value || 0)
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
            this.getFinanceStatistics(),
            this.getRevenueExpensesTrends(),
            this.getPaymentStatusBreakdown(),
            this.getCashFlowTrends(),
        ])
    }

    async getFinanceStatistics() {
        try {
            console.log("Fetching finance statistics with dates:", this.state.start_date, this.state.end_date)
            const stats = await this.orm.call(
                "account.move",
                "get_finance_statistics",
                [this.state.start_date || null, this.state.end_date || null]
            )
            
            console.log("Finance statistics received:", stats)
            
            if (stats) {
                this.state.total_revenue.value = stats.total_revenue || 0.0
                this.state.net_revenue.value = stats.net_revenue || 0.0
                this.state.total_expenses.value = stats.total_expenses || 0.0
                this.state.net_expenses.value = stats.net_expenses || 0.0
                this.state.profit.value = stats.profit || 0.0
                this.state.accounts_receivable.value = stats.accounts_receivable || 0.0
                this.state.accounts_payable.value = stats.accounts_payable || 0.0
                this.state.cash_inflow.value = stats.cash_inflow || 0.0
                this.state.cash_outflow.value = stats.cash_outflow || 0.0
                this.state.net_cash_flow.value = stats.net_cash_flow || 0.0
                this.state.total_invoices.value = stats.total_invoices || 0
                this.state.paid_invoices_count.value = stats.paid_invoices_count || 0
                this.state.unpaid_invoices_count.value = stats.unpaid_invoices_count || 0
                this.state.total_bills.value = stats.total_bills || 0
                this.state.paid_bills_count.value = stats.paid_bills_count || 0
                this.state.unpaid_bills_count.value = stats.unpaid_bills_count || 0
                
                // Get currency symbol from stats
                const currency = stats.currency_symbol || ''
                this.state.total_revenue.currency = currency
                this.state.net_revenue.currency = currency
                this.state.total_expenses.currency = currency
                this.state.net_expenses.currency = currency
                this.state.profit.currency = currency
                this.state.accounts_receivable.currency = currency
                this.state.accounts_payable.currency = currency
                this.state.cash_inflow.currency = currency
                this.state.cash_outflow.currency = currency
                this.state.net_cash_flow.currency = currency
            } else {
                console.warn("No finance statistics data received")
            }
        } catch (error) {
            console.error("Error loading finance statistics:", error)
            console.error("Error details:", error.message, error.stack)
        }
    }

    async getRevenueExpensesTrends() {
        try {
            console.log("Fetching revenue/expenses trends with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "account.move",
                "get_revenue_expenses_trends",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Revenue/expenses trends data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.revenue_expenses_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Revenue/expenses chart updated")
            } else {
                console.warn("Invalid revenue/expenses trends data:", chartData)
                this.state.revenue_expenses_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading revenue/expenses trends:", error)
            this.state.revenue_expenses_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getPaymentStatusBreakdown() {
        try {
            console.log("Fetching payment status breakdown with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "account.move",
                "get_payment_status_breakdown",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Payment status breakdown data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.payment_status_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Payment status chart updated")
            } else {
                console.warn("Invalid payment status breakdown data:", chartData)
                this.state.payment_status_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading payment status breakdown:", error)
            this.state.payment_status_chart = {
                labels: [],
                datasets: [],
            }
        }
    }

    async getCashFlowTrends() {
        try {
            console.log("Fetching cash flow trends with dates:", this.state.start_date, this.state.end_date)
            const chartData = await this.orm.call(
                "account.move",
                "get_cash_flow_trends",
                [this.state.start_date || null, this.state.end_date || null]
            )

            console.log("Cash flow trends data received:", chartData)

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.cash_flow_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
                console.log("Cash flow chart updated")
            } else {
                console.warn("Invalid cash flow trends data:", chartData)
                this.state.cash_flow_chart = {
                    labels: [],
                    datasets: [],
                }
            }
        } catch (error) {
            console.error("Error loading cash flow trends:", error)
            this.state.cash_flow_chart = {
                labels: [],
                datasets: [],
            }
        }
    }
}

FinanceDashboard.template = "finance_dashboard.FinanceDashboard"
FinanceDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("finance_dashboard.finance_dashboard", FinanceDashboard)

