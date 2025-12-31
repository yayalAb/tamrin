# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    repair_job_card_id = fields.Many2one(
        'repair.order',
        string='Repair Job Card',
        help='Related repair job card',
        ondelete='set null',
        copy=False,
        required=False,
        readonly=False,
    )
    
    def unlink(self):
        """Override unlink to handle repair_job_card_id foreign key constraint"""
        # Clear the repair_job_card_id field before deletion to avoid foreign key constraint issues
        # This ensures the foreign key constraint doesn't prevent deletion
        if self.repair_job_card_id:
            self.write({'repair_job_card_id': False})
        return super(SaleOrder, self).unlink()

