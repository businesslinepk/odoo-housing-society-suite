from odoo import models, fields

class HousingSociety(models.Model):
    _name = "housing.society"
    _description = "Housing Society"

    name = fields.Char(required=True)
    city = fields.Char()
