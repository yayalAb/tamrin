/** @odoo-module **/

import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onPatched } = owl;

export class ChartRenderer extends Component {
    static template = "inventory_dashboard.ChartRenderer";

    setup() {
        this.chartRef = useRef("chart");
        this.chartInstance = null;

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
        });

        onMounted(() => this.renderChart());
        onPatched(() => this.updateChart());
    }

    renderChart() {
        if (!this.chartRef.el || !window.Chart) {
            console.error("Chart.js or canvas not available");
            return;
        }

        // Validate props.data before rendering
        if (!this.props.data || !this.props.data.labels || !this.props.data.datasets || this.props.data.datasets.length === 0) {
            console.warn("Invalid chart data or empty datasets:", this.props.data);
            return;
        }

        const ctx = this.chartRef.el.getContext("2d");
        
        // Destroy existing chart if it exists
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }
        
        // Check if we need dual y-axis (for mixed charts)
        const hasDualAxis = this.props.data.datasets.some(ds => ds.yAxisID);
        
        const chartConfig = {
            type: this.props.type || "bar",
            data: this.props.data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { 
                        display: !!this.props.title, 
                        text: this.props.title || "" 
                    },
                    legend: { display: true, position: "top" },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { 
                            display: !!this.props.y_title, 
                            text: this.props.y_title || "" 
                        },
                        position: 'left',
                    },
                    ...(hasDualAxis && {
                        y1: {
                            beginAtZero: true,
                            title: { 
                                display: !!this.props.y1_title, 
                                text: this.props.y1_title || "" 
                            },
                            position: 'right',
                            grid: {
                                drawOnChartArea: false,
                            },
                        },
                    }),
                    x: {
                        title: { 
                            display: !!this.props.x_title, 
                            text: this.props.x_title || "" 
                        },
                    },
                },
            },
        };
        
        this.chartInstance = new Chart(ctx, chartConfig);
    }

    updateChart() {
        if (this.chartInstance) {
            // Validate props.data before updating
            if (!this.props.data || !this.props.data.labels || !this.props.data.datasets || this.props.data.datasets.length === 0) {
                console.warn("Invalid chart data for update or empty datasets:", this.props.data);
                // Destroy chart if data is invalid
                if (this.chartInstance) {
                    this.chartInstance.destroy();
                    this.chartInstance = null;
                }
                return;
            }
            this.chartInstance.data = this.props.data;
            this.chartInstance.update();
        } else {
            // If chart doesn't exist, try to render it
            this.renderChart();
        }
    }
}

