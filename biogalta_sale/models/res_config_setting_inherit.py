# -*- coding: utf-8 -*-

from odoo import fields, models

class res_config_setting(models.TransientModel):
    _inherit = 'res.config.settings'
    
    observation_machine = fields.Text(related='company_id.observation_machine', string="Observation (Machine)", readonly=False)

class ResCompany(models.Model):
    _inherit = "res.company"

    observation_machine = fields.Text(string='Observation', translate=True)
