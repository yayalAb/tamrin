# -*- coding: utf-8 -*-

from odoo import models, fields


class EmployeeReportWizard(models.TransientModel):
    _name = 'employee.report.wizard'
    _description = 'Employee Report Wizard'

    department_ids = fields.Many2many(
        'hr.department',
        string='Departments/Offices',
        help='Leave empty to include all departments'
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees',
        help='Leave empty to include all employees'
    )

    def action_generate_report(self):
        """
        Generate the employee report
        """
        self.ensure_one()
        
        # Refresh the view
        self.env['employee.report.summary'].init()
        
        # Build domain with filters
        domain = []
        
        if self.department_ids:
            domain.append(('office', 'in', self.department_ids.mapped('name')))
        if self.employee_ids:
            domain.append(('employee_id', 'in', self.employee_ids.ids))
        
        # Get records based on domain
        records = self.env['employee.report.summary'].search(domain)
        
        # Return PDF report action
        return self.env.ref('custom_report.action_employee_report').report_action(records)


