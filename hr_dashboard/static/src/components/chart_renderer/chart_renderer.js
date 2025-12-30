/** @odoo-module **/

import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted, onPatched } = owl;

export class ChartRenderer extends Component {
    static template = "hr_dashboard.ChartRenderer";

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
        
        // Prepare chart data - add net line dataset if requested
        let chartData = { ...this.props.data };
        if (this.props.showNetLine && chartData.labels && chartData.labels.length > 0) {
            // Add a horizontal line at y=0 as a separate dataset
            const netLineData = new Array(chartData.labels.length).fill(0);
            chartData.datasets = [
                ...chartData.datasets,
                {
                    label: 'Net Line',
                    data: netLineData,
                    borderColor: 'rgba(0, 0, 0, 0.5)',
                    backgroundColor: 'rgba(0, 0, 0, 0)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    fill: false,
                    tension: 0,
                    order: 999, // Draw on top
                }
            ];
        }

        this.chartInstance = new Chart(ctx, {
            type: this.props.type || "bar",
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { 
                        display: !!this.props.title, 
                        text: this.props.title || "" 
                    },
                    legend: { 
                        display: true, 
                        position: "top",
                        // Hide net line from legend if it exists
                        filter: (legendItem) => {
                            return legendItem.text !== 'Net Line';
                        }
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { 
                            display: !!this.props.y_title, 
                            text: this.props.y_title || "" 
                        },
                    },
                    x: {
                        title: { 
                            display: !!this.props.x_title, 
                            text: this.props.x_title || "" 
                        },
                    },
                },
            },
        });
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
            
            // Prepare chart data - add net line dataset if requested
            let chartData = { ...this.props.data };
            if (this.props.showNetLine && chartData.labels && chartData.labels.length > 0) {
                // Check if net line already exists
                const hasNetLine = chartData.datasets.some(ds => ds.label === 'Net Line');
                if (!hasNetLine) {
                    // Add a horizontal line at y=0 as a separate dataset
                    const netLineData = new Array(chartData.labels.length).fill(0);
                    chartData.datasets = [
                        ...chartData.datasets,
                        {
                            label: 'Net Line',
                            data: netLineData,
                            borderColor: 'rgba(0, 0, 0, 0.5)',
                            backgroundColor: 'rgba(0, 0, 0, 0)',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            pointRadius: 0,
                            pointHoverRadius: 0,
                            fill: false,
                            tension: 0,
                            order: 999, // Draw on top
                        }
                    ];
                }
            }
            
            this.chartInstance.data = chartData;
            this.chartInstance.update();
        } else {
            // If chart doesn't exist, try to render it
            this.renderChart();
        }
    }
}

