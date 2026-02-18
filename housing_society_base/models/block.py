from odoo import models, fields

class HousingBlock(models.Model):
    _name = "housing.block"
    _description = "Housing Block"

    name = fields.Char(required=True)
    society_id = fields.Many2one("housing.society", required=True)
