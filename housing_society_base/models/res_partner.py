from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_housing_member = fields.Boolean(string="Housing Member")
    membership_no = fields.Char(string="Membership No")

    plot_ids = fields.One2many(
        "housing.plot",
        "owner_id",
        string="Owned Plots"
    )
