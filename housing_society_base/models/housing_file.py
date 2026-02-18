from odoo import models, fields

class HousingFile(models.Model):
    _name = "housing.file"
    _description = "Housing File"
    _rec_name = "file_no"

    file_no = fields.Char(string="File No", required=True)
    file_type = fields.Selection(
        [("residential", "Residential"),
         ("commercial", "Commercial")],

    
        required=True
    )
    size_sq_yards = fields.Char(string="File Size (Sq Yards)")

    status = fields.Selection(
        [("active", "Active"), ("allotted", "Plot Allotted")],
        default="active"
    )
