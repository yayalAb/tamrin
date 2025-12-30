# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def get_employee_inventory_data(self):
        """Get employee inventory data for the last 12 months based on contract start date and type"""
        try:
            labels = []
            total_data = []
            
            # Color mapping for specific contract types (less bold colors)
            contract_type_colors = {
                'permanent': {'bg': 'rgba(156, 39, 176, 0.5)', 'border': 'rgba(156, 39, 176, 0.8)'},  # Soft Purple
                'temporary': {'bg': 'rgba(255, 152, 0, 0.5)', 'border': 'rgba(255, 152, 0, 0.8)'},  # Soft Orange
                'seasonal': {'bg': 'rgba(255, 87, 34, 0.5)', 'border': 'rgba(255, 87, 34, 0.8)'},  # Soft Deep Orange
                'full-time': {'bg': 'rgba(76, 175, 80, 0.5)', 'border': 'rgba(76, 175, 80, 0.8)'},  # Soft Green
                'fulltime': {'bg': 'rgba(76, 175, 80, 0.5)', 'border': 'rgba(76, 175, 80, 0.8)'},  # Soft Green (alternative)
                'part-time': {'bg': 'rgba(233, 30, 99, 0.5)', 'border': 'rgba(233, 30, 99, 0.8)'},  # Soft Pink
                'parttime': {'bg': 'rgba(233, 30, 99, 0.5)', 'border': 'rgba(233, 30, 99, 0.8)'},  # Soft Pink (alternative)
            }
            
            # Fallback color palette for any other contract types (less bold)
            fallback_colors = [
                {'bg': 'rgba(33, 150, 243, 0.5)', 'border': 'rgba(33, 150, 243, 0.8)'},  # Soft Blue
                {'bg': 'rgba(0, 188, 212, 0.5)', 'border': 'rgba(0, 188, 212, 0.8)'},  # Soft Cyan
                {'bg': 'rgba(63, 81, 181, 0.5)', 'border': 'rgba(63, 81, 181, 0.8)'},  # Soft Indigo
            ]
            
            # Dictionary to store data for each contract type dynamically
            contract_type_data = {}
            
            # Check if contract_type_id field exists in hr.contract (Many2one field)
            contract_model = self.env['hr.contract']
            has_contract_type_id = 'contract_type_id' in contract_model._fields

            # First pass: collect all unique contract types
            all_contract_types = set()
            
            # Get all contracts to discover all contract types
            all_contracts = self.env['hr.contract'].search([
                ('state', 'in', ['open', 'close'])
            ])
            
            for contract in all_contracts:
                if has_contract_type_id:
                    # contract_type_id is a Many2one field, get the name
                    if contract.contract_type_id:
                        contract_type_name = contract.contract_type_id.name
                        if contract_type_name:
                            contract_type_str = str(contract_type_name).lower()
                        else:
                            contract_type_str = 'none'
                    else:
                        # If contract_type_id is None/False, treat as 'none'
                        contract_type_str = 'none'
                    
                    all_contract_types.add(contract_type_str)
                    # Initialize data list for this contract type
                    if contract_type_str not in contract_type_data:
                        contract_type_data[contract_type_str] = []

            for i in range(11, -1, -1):
                month_date = datetime.now() - timedelta(days=30 * i)
                month_start = month_date.replace(day=1)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                # Get contracts that were active during this month
                try:
                    contracts = self.env['hr.contract'].search([
                        ('state', 'in', ['open', 'close']),
                        ('date_start', '<=', month_end.strftime('%Y-%m-%d')),
                        '|',
                        ('date_end', '>=', month_start.strftime('%Y-%m-%d')),
                        ('date_end', '=', False)
                    ])
                except Exception:
                    contracts = self.env['hr.contract'].search([
                        ('state', 'in', ['open', 'close']),
                        ('date_start', '<=', month_end.strftime('%Y-%m-%d'))
                    ])

                # Count unique employees by contract type
                total_employees = set()
                
                # Initialize data structures for this month
                month_contract_types = {}

                for contract in contracts:
                    try:
                        if not contract.employee_id or not contract.employee_id.active:
                            continue
                            
                        emp_id = contract.employee_id.id
                        total_employees.add(emp_id)
                        
                        # Dynamic contract type detection using contract_type_id (Many2one)
                        if has_contract_type_id:
                            # contract_type_id is a Many2one field, get the name
                            if contract.contract_type_id:
                                contract_type_name = contract.contract_type_id.name
                                if contract_type_name:
                                    contract_type_str = str(contract_type_name).lower()
                                else:
                                    contract_type_str = 'none'
                            else:
                                # If contract_type_id is None/False, treat as 'none'
                                contract_type_str = 'none'
                            
                            if contract_type_str not in month_contract_types:
                                month_contract_types[contract_type_str] = set()
                            month_contract_types[contract_type_str].add(emp_id)
                    except Exception as e:
                        # Log error but continue processing
                        import logging
                        _logger = logging.getLogger(__name__)
                        _logger.warning("Error processing contract %s: %s", contract.id if contract else 'unknown', str(e))
                        continue

                labels.append(month_date.strftime('%b'))
                total_data.append(len(total_employees))
                
                # Append counts for each contract type (initialize with 0 if not found)
                for contract_type_str in all_contract_types:
                    if contract_type_str not in contract_type_data:
                        contract_type_data[contract_type_str] = []
                    count = len(month_contract_types.get(contract_type_str, set()))
                    contract_type_data[contract_type_str].append(count)

            # Build datasets dynamically
            datasets = [
                {
                    'label': 'Total',
                    'data': total_data,
                    'backgroundColor': 'rgba(33, 150, 243, 0.5)',
                    'borderColor': 'rgba(33, 150, 243, 0.8)',
                    'borderWidth': 1,
                },
            ]
            
            # Add contract type datasets dynamically for all contract types found
            color_index = 0
            
            for contract_type_str, data_list in sorted(contract_type_data.items()):
                contract_type_lower = contract_type_str.lower()
                # Only add if there's data for this contract type
                if any(data_list):
                    # Get color from mapping or use fallback
                    if contract_type_lower in contract_type_colors:
                        color = contract_type_colors[contract_type_lower]
                    else:
                        # Use fallback color for other types
                        color = fallback_colors[color_index % len(fallback_colors)]
                        color_index += 1
                    
                    # Format label: capitalize and replace underscores/hyphens
                    # Handle 'none' specially
                    if contract_type_lower == 'none':
                        label = 'No Contract Type'
                    else:
                        # Capitalize first letter of each word
                        label = contract_type_str.replace('_', ' ').replace('-', ' ').title()
                    
                    datasets.append({
                        'label': label,
                        'data': data_list,
                        'backgroundColor': color['bg'],
                        'borderColor': color['border'],
                        'borderWidth': 1,
                    })

            return {
                'labels': labels,
                'datasets': datasets,
            }
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Error in get_employee_inventory_data: %s", str(e))
            # Return empty data structure on error
            return {
                'labels': [],
                'datasets': [],
            }

    @api.model
    def get_department_headcount_data(self):
        """Get department headcount data"""
        employees = self.search([('active', '=', True)])
        dept_data = {}

        for emp in employees:
            dept_name = emp.department_id.name if emp.department_id else 'No Department'
            dept_data[dept_name] = dept_data.get(dept_name, 0) + 1

        labels = list(dept_data.keys())
        data = list(dept_data.values())

        return {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Employees per Department',
                    'data': data,
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(199, 199, 199, 0.6)',
                        'rgba(83, 102, 255, 0.6)',
                        'rgba(255, 99, 255, 0.6)',
                        'rgba(99, 255, 132, 0.6)',
                        'rgba(255, 206, 99, 0.6)',
                        'rgba(54, 162, 99, 0.6)',
                    ],
                    'borderColor': [
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(199, 199, 199, 1)',
                        'rgba(83, 102, 255, 1)',
                        'rgba(255, 99, 255, 1)',
                        'rgba(99, 255, 132, 1)',
                        'rgba(255, 206, 99, 1)',
                        'rgba(54, 162, 99, 1)',
                    ],
                    'borderWidth': 1,
                },
            ],
        }

