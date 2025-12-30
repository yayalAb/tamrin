# -*- coding: utf-8 -*-

from odoo import fields, models


class EmployeeReportSummary(models.Model):
    _name = "employee.report.summary"
    _description = "Employee Report Summary"
    _auto = False
    _order = "employee_name"

    sequence = fields.Integer(string="SN.", readonly=True)
    employee_id = fields.Many2one("hr.employee", string="Employee", readonly=True)
    employee_name = fields.Char(string="Employee Name", readonly=True)
    office = fields.Char(string="Office", readonly=True)
    hiring_date = fields.Date(string="Hiring Date", readonly=True)
    education = fields.Char(string="Education", readonly=True)
    edu_level = fields.Char(string="Edu Level", readonly=True)
    work_experience_tamrin = fields.Float(string="Work Experience at Tamrin", readonly=True)
    work_experience_before = fields.Float(string="Work Experience Before Tamrin", readonly=True)
    total_experience = fields.Float(string="Total Experience", readonly=True)
    basic_salary = fields.Float(string="Basic Salary", readonly=True, digits="Account")

    def init(self):
        # Extract employee data with work experience calculations
        # Using standard HR fields only
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW employee_report_summary AS (
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY emp.id) AS id,
                    ROW_NUMBER() OVER (ORDER BY emp.id) AS sequence,
                    emp.id AS employee_id,
                    COALESCE(emp.name::text, '') AS employee_name,
                    COALESCE(
                        CASE 
                            WHEN dept.name IS NULL THEN ''
                            WHEN jsonb_typeof(dept.name) = 'object' THEN 
                                COALESCE(
                                    dept.name->>'en_US',
                                    dept.name->>'en',
                                    dept.name->>'ar',
                                    dept.name->>'fr_FR',
                                    (SELECT value FROM jsonb_each_text(dept.name) LIMIT 1)
                                )
                            ELSE dept.name::text
                        END,
                        ''
                    ) AS office,
                    contract_data.hiring_date AS hiring_date,
                    COALESCE(emp.study_field::text, '') AS education,
                    COALESCE(emp.study_school::text, '') AS edu_level,
                    CASE 
                        WHEN contract_data.hiring_date IS NOT NULL THEN 
                            EXTRACT(YEAR FROM AGE(CURRENT_DATE, contract_data.hiring_date)) * 12 + 
                            EXTRACT(MONTH FROM AGE(CURRENT_DATE, contract_data.hiring_date))
                        ELSE 0
                    END / 12.0 AS work_experience_tamrin,
                    0.0 AS work_experience_before,
                    CASE 
                        WHEN contract_data.hiring_date IS NOT NULL THEN 
                            EXTRACT(YEAR FROM AGE(CURRENT_DATE, contract_data.hiring_date)) * 12 + 
                            EXTRACT(MONTH FROM AGE(CURRENT_DATE, contract_data.hiring_date))
                        ELSE 0
                    END / 12.0 AS total_experience,
                    COALESCE(contract_data.basic_salary, 0.0) AS basic_salary
                FROM hr_employee emp
                LEFT JOIN hr_department dept ON emp.department_id = dept.id
                LEFT JOIN (
                    SELECT 
                        employee_id,
                        MIN(date_start) AS hiring_date,
                        MAX(wage) AS basic_salary
                    FROM hr_contract
                    WHERE state IN ('open', 'close')
                    GROUP BY employee_id
                ) contract_data ON emp.id = contract_data.employee_id
                WHERE emp.active = True
            )
        """)

