from odoo import models, fields

class PlotAllotment(models.Model):
    _name = "housing.plot.allotment"
    _description = "Plot Allotment"

    member_id = fields.Many2one(
        "housing.member",
        string="Member",
        required=True
    )

    plot_id = fields.Many2one(
        "housing.plot",
        string="Plot",
        required=True
    )

    allotment_date = fields.Date(
        string="Allotment Date",
        default=fields.Date.today,
        required=True
    )

    remarks = fields.Text(string="Remarks")

    state = fields.Selection([
        ("active", "Active"),
        ("cancelled", "Cancelled"),
    ], default="active")
