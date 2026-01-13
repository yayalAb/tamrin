/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class InventoryDashboard extends Component {
    setup() {
        this.state = useState({
            total_products: { value: 0 },
            products_with_stock: { value: 0 },
            low_stock_products: { value: 0 },
            out_of_stock_products: { value: 0 },
            total_stock_value: { value: 0, currency: '' },
            total_locations: { value: 0 },
            category_stock_chart: {
                labels: [],
                datasets: [],
            },
            category_value_chart: {
                labels: [],
                datasets: [],
            },
            top_products_chart: {
                labels: [],
                datasets: [],
            },
            location_chart: {
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
        this.onTotalProductsClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Products",
                res_model: "product.product",
                views: [[false, "list"], [false, "form"]],
                domain: [['type', '!=', 'service']],
                target: "current",
            })
        }

        this.onProductsWithStockClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Products with Stock",
                res_model: "product.product",
                views: [[false, "list"], [false, "form"]],
                domain: [
                    ['type', '!=', 'service'],
                    ['qty_available', '>', 0]
                ],
                target: "current",
            })
        }

        this.onLowStockClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Low Stock Products",
                res_model: "product.product",
                views: [[false, "list"], [false, "form"]],
                domain: [
                    ['type', '!=', 'service'],
                    ['qty_available', '>', 0],
                    ['qty_available', '<', 10]
                ],
                target: "current",
            })
        }

        this.onOutOfStockClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Out of Stock Products",
                res_model: "product.product",
                views: [[false, "list"], [false, "form"]],
                domain: [
                    ['type', '!=', 'service'],
                    ['qty_available', '<=', 0]
                ],
                target: "current",
            })
        }

        this.onTotalLocationsClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Warehouse Locations",
                res_model: "stock.location",
                views: [[false, "list"], [false, "form"]],
                domain: [['usage', '=', 'internal']],
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
        this.getTotalStockValueFormatted = () => {
            const currency = this.state.total_stock_value.currency || ''
            const amount = this.formatCurrency(this.state.total_stock_value.value || 0)
            return `${currency} ${amount}`
        }
    }

    async refreshData() {
        await Promise.all([
            this.getInventoryStatistics(),
            this.getCategoryStock(),
            this.getCategoryStockValue(),
            this.getTopProductsByValue(),
            this.getLocationStock(),
        ])
    }

    async getInventoryStatistics() {
        try {
            const stats = await this.orm.call(
                "product.product",
                "get_inventory_statistics",
                []
            )
            
            this.state.total_products.value = stats.total_products || 0
            this.state.products_with_stock.value = stats.products_with_stock || 0
            this.state.low_stock_products.value = stats.low_stock_products || 0
            this.state.out_of_stock_products.value = stats.out_of_stock_products || 0
            this.state.total_stock_value.value = stats.total_stock_value || 0.0
            this.state.total_locations.value = stats.total_locations || 0
            
            // Get currency symbol from stats
            this.state.total_stock_value.currency = stats.currency_symbol || ''
        } catch (error) {
            console.error("Error loading inventory statistics:", error)
        }
    }

    async getCategoryStock() {
        try {
            const chartData = await this.orm.call(
                "product.product",
                "get_category_stock",
                []
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.category_stock_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading category stock:", error)
        }
    }

    async getCategoryStockValue() {
        try {
            const chartData = await this.orm.call(
                "product.product",
                "get_category_stock_value",
                []
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.category_value_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading category stock value:", error)
        }
    }

    async getTopProductsByValue() {
        try {
            const chartData = await this.orm.call(
                "product.product",
                "get_top_products_by_value",
                []
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.top_products_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading top products:", error)
        }
    }

    async getLocationStock() {
        try {
            const chartData = await this.orm.call(
                "stock.quant",
                "get_location_stock",
                []
            )

            if (chartData && chartData.labels && chartData.datasets) {
                this.state.location_chart = {
                    labels: chartData.labels || [],
                    datasets: chartData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading location stock:", error)
        }
    }
}

InventoryDashboard.template = "inventory_dashboard.InventoryDashboard"
InventoryDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("inventory_dashboard.inventory_dashboard", InventoryDashboard)


