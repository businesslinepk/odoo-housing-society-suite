from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_residential = fields.Boolean(string="Enable Residential")
    enable_commercial = fields.Boolean(string="Enable Commercial")
    enable_towers = fields.Boolean(string="Enable Towers")
    enable_apartments = fields.Boolean(string="Enable Apartments / Flats")
    enable_shops = fields.Boolean(string="Enable Shops")
    enable_offices = fields.Boolean(string="Enable Offices")
    enable_transfer = fields.Boolean(string="Enable Transfer")
    enable_portal = fields.Boolean(string="Enable Customer Portal")


    enable_towers = fields.Boolean(
        string="Enable Towers",
        config_parameter='housing.enable_towers'
    )

    def set_values(self):
        super().set_values()
        group = self.env.ref('housing_society_base.group_housing_tower')
        if self.enable_towers:
            group.users = [(4, self.env.uid)]
        else:
            group.users = [(3, self.env.uid)]