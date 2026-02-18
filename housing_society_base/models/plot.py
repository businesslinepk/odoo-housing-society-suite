from odoo import models, fields


class HousingPlot(models.Model):
    _name = "housing.plot"
    _description = "Housing Plot"
    _rec_name = "plot_no"

   
    plot_no = fields.Char(string="Plot No", required="true")
    plot_type = fields.Selection(
        [
            ("residential", "Residential"),
            ("commercial", "Commercial"),
        ],
        string="Plot Type",
        required=True,
        default="residential"
    )

    block_id = fields.Many2one(
        "housing.block",
        string="Block",
        required=True
    )
    street_no = fields.Char(string="Street No")
    size_sq_yards = fields.Char(string="Size (Sq. Yards)")

    status = fields.Selection(
    [
        ("available", "Available"),
        ("allotted", "Allotted"),
        ("cancelled", "Cancelled"),
    ],
    default="available",
    string="Status"
)
def name_get(self):
     result = []
     for rec in self:
        name = rec.plot_no or rec.id
        if rec.block_id:
            name = f"{rec.block_id.name} / Plot {name}"
        result.append((rec.id, name))
     return result

 
