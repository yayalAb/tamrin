/** @odoo-module **/

import { registry } from "@web/core/registry"
import { DashboardCard } from "./dashboard_card/dashboard_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { useService } from "@web/core/utils/hooks"

const { Component, onWillStart, useState } = owl

export class HRDashboard extends Component {
    setup() {
        // Set default dates to current month
        const today = new Date()
        const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        
        this.state = useState({
            start_date: firstDayOfMonth.toISOString().split('T')[0],
            end_date: today.toISOString().split('T')[0],
            total_employees: { value: 0 },
            expiring_contracts: { value: 0 },
            total_leaves: { value: 0 },
            total_appraisals: { value: 0 },
            total_recruitments: { value: 0 },
            total_resignations: { value: 0 },
            inventory_chart: {
                labels: [],
                datasets: [
                    {
                        label: "Total Employees",
                        data: [],
                        backgroundColor: "rgba(54, 162, 235, 0.6)",
                        borderColor: "rgba(54, 162, 235, 1)",
                        borderWidth: 1,
                    },
                    {
                        label: "Permanent",
                        data: [],
                        backgroundColor: "rgba(153, 102, 255, 0.6)",
                        borderColor: "rgba(153, 102, 255, 1)",
                        borderWidth: 1,
                    },
                    {
                        label: "Contract",
                        data: [],
                        backgroundColor: "rgba(75, 192, 192, 0.6)",
                        borderColor: "rgba(75, 192, 192, 1)",
                        borderWidth: 1,
                    },
                ],
            },
            payroll_chart: {
                labels: [],
                datasets: [
                    {
                        label: "Gross Payroll by Month",
                        data: [],
                        borderColor: "rgb(255, 99, 132)",
                        backgroundColor: "rgba(255, 99, 132, 0.2)",
                        tension: 0.1,
                    },
                ],
            },
            dept_chart: {
                labels: [],
                datasets: [
                    {
                        label: "Employees per Department",
                        data: [],
                        backgroundColor: [
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(255, 206, 86, 0.6)",
                            "rgba(75, 192, 192, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(153, 102, 255, 0.6)",
                            "rgba(255, 159, 64, 0.6)",
                            "rgba(199, 199, 199, 0.6)",
                            "rgba(83, 102, 255, 0.6)",
                            "rgba(255, 99, 255, 0.6)",
                            "rgba(99, 255, 132, 0.6)",
                            "rgba(255, 206, 99, 0.6)",
                            "rgba(54, 162, 99, 0.6)",
                        ],
                        borderColor: [
                            "rgba(255, 99, 132, 1)",
                            "rgba(255, 206, 86, 1)",
                            "rgba(75, 192, 192, 1)",
                            "rgba(54, 162, 235, 1)",
                            "rgba(153, 102, 255, 1)",
                            "rgba(255, 159, 64, 1)",
                            "rgba(199, 199, 199, 1)",
                            "rgba(83, 102, 255, 1)",
                            "rgba(255, 99, 255, 1)",
                            "rgba(99, 255, 132, 1)",
                            "rgba(255, 206, 99, 1)",
                            "rgba(54, 162, 99, 1)",
                        ],
                        borderWidth: 1,
                    },
                ],
            },
            appraisal_chart: {
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
        this.onTotalEmployeesClick = () => {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Employees",
                res_model: "hr.employee",
                views: [[false, "list"], [false, "form"]],
                domain: [["active", "=", true]],
                target: "current",
            })
        }

        this.onExpiringContractsClick = () => {
            const domain = [
                ["state", "in", ["open", "close"]],
            ]
            if (this.state.start_date) {
                domain.push(["date_end", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_end", "<=", this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Expiring Contracts",
                res_model: "hr.contract",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalLeavesClick = () => {
            const domain = []
            if (this.state.start_date) {
                domain.push(["date_from", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_from", "<=", this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Leave Requests",
                res_model: "hr.leave",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalAppraisalsClick = () => {
            const domain = []
            if (this.state.start_date) {
                domain.push(["date_close", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_close", "<=", this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Appraisals",
                res_model: "hr.appraisal",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalRecruitmentsClick = () => {
            const domain = []
            if (this.state.start_date) {
                domain.push(["create_date", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["create_date", "<=", this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Recruitments",
                res_model: "hr.applicant",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
        }

        this.onTotalResignationsClick = () => {
            const domain = [["active", "=", false]]
            if (this.state.start_date) {
                domain.push(["write_date", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["write_date", "<=", this.state.end_date])
            }
            this.action.doAction({
                type: "ir.actions.act_window",
                name: "Resignations",
                res_model: "hr.employee",
                views: [[false, "list"], [false, "form"]],
                domain: domain,
                target: "current",
            })
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
            this.getTotalEmployees(),
            this.getExpiringContracts(),
            this.getTotalLeaves(),
            this.getTotalAppraisals(),
            this.getTotalRecruitments(),
            this.getTotalResignations(),
            this.getEmployeeInventory(),
            this.getMonthlyPayroll(),
            this.getDepartmentHeadcount(),
        ])
    }

    async getTotalEmployees() {
        try {
            const count = await this.orm.searchCount("hr.employee", [["active", "=", true]])
            this.state.total_employees.value = count || 0
        } catch (error) {
            console.error("Error loading total employees:", error)
            this.state.total_employees.value = 0
        }
    }

    async getExpiringContracts() {
        try {
            const domain = [
                ["state", "in", ["open", "close"]],
            ]
            if (this.state.start_date) {
                domain.push(["date_end", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_end", "<=", this.state.end_date])
            }
            const count = await this.orm.searchCount("hr.contract", domain)
            this.state.expiring_contracts.value = count || 0
        } catch (error) {
            console.error("Error loading expiring contracts:", error)
            this.state.expiring_contracts.value = 0
        }
    }

    async getTotalLeaves() {
        try {
            const domain = []
            if (this.state.start_date) {
                domain.push(["date_from", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_from", "<=", this.state.end_date])
            }
            const count = await this.orm.searchCount("hr.leave", domain)
            this.state.total_leaves.value = count || 0
        } catch (error) {
            console.error("Error loading total leaves:", error)
            this.state.total_leaves.value = 0
        }
    }

    async getTotalAppraisals() {
        try {
            const domain = []
            if (this.state.start_date) {
                domain.push(["date_close", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["date_close", "<=", this.state.end_date])
            }
            const count = await this.orm.searchCount("hr.appraisal", domain)
            this.state.total_appraisals.value = count || 0
        } catch (error) {
            console.error("Error loading total appraisals:", error)
            this.state.total_appraisals.value = 0
        }
    }

    async getTotalRecruitments() {
        try {
            const domain = []
            if (this.state.start_date) {
                domain.push(["create_date", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["create_date", "<=", this.state.end_date])
            }
            const count = await this.orm.searchCount("hr.applicant", domain)
            this.state.total_recruitments.value = count || 0
        } catch (error) {
            console.error("Error loading total recruitments:", error)
            this.state.total_recruitments.value = 0
        }
    }

    async getTotalResignations() {
        try {
            const domain = [["active", "=", false]]
            if (this.state.start_date) {
                domain.push(["write_date", ">=", this.state.start_date])
            }
            if (this.state.end_date) {
                domain.push(["write_date", "<=", this.state.end_date])
            }
            const count = await this.orm.searchCount("hr.employee", domain)
            this.state.total_resignations.value = count || 0
        } catch (error) {
            console.error("Error loading total resignations:", error)
            this.state.total_resignations.value = 0
        }
    }

    async getEmployeeInventory() {
        try {
            const inventoryData = await this.orm.call(
                "hr.employee",
                "get_employee_inventory_data",
                []
            )

            if (inventoryData && inventoryData.labels && inventoryData.datasets) {
                this.state.inventory_chart = {
                    labels: inventoryData.labels || [],
                    datasets: inventoryData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading employee inventory:", error)
        }
    }

    async getMonthlyPayroll() {
        try {
            const payrollData = await this.orm.call(
                "hr.contract",
                "get_monthly_payroll_data",
                []
            )

            if (payrollData && payrollData.labels && payrollData.datasets) {
                this.state.payroll_chart = {
                    labels: payrollData.labels || [],
                    datasets: payrollData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading monthly payroll:", error)
        }
    }

    async getDepartmentHeadcount() {
        try {
            const deptData = await this.orm.call(
                "hr.employee",
                "get_department_headcount_data",
                []
            )

            if (deptData && deptData.labels && deptData.datasets) {
                this.state.dept_chart = {
                    labels: deptData.labels || [],
                    datasets: deptData.datasets || [],
                }
            }
        } catch (error) {
            console.error("Error loading department headcount:", error)
        }
    }
}

HRDashboard.template = "hr_dashboard.HRDashboard"
HRDashboard.components = { DashboardCard, ChartRenderer }

registry
    .category("actions")
    .add("hr_dashboard.hr_dashboard", HRDashboard)

