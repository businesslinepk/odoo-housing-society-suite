from odoo import models, fields

class HousingNominee(models.Model):
    _name = "housing.nominee"
    _description = "Housing Nominee"

    member_id = fields.Many2one("housing.member", string="Member", ondelete="cascade")
    name = fields.Char(required=True)
    cnic = fields.Char()
    relation = fields.Char()
