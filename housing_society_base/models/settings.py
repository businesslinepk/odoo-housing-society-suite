from odoo import models, fields

class HousingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_residential = fields.Boolean(string="Enable Residential")
    enable_commercial = fields.Boolean(string="Enable Commercial")
    enable_towers = fields.Boolean(string="Enable Towers")
    enable_apartments = fields.Boolean(string="Enable Apartments / Flats")
    enable_shops = fields.Boolean(string="Enable Shops")
    enable_offices = fields.Boolean(string="Enable Offices")
    enable_transfer = fields.Boolean(string="Enable Transfer Process")
    enable_portal = fields.Boolean(string="Enable Customer Portal")

    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('housing.enable_residential', self.enable_residential)
        param.set_param('housing.enable_commercial', self.enable_commercial)
        param.set_param('housing.enable_towers', self.enable_towers)
        param.set_param('housing.enable_apartments', self.enable_apartments)
        param.set_param('housing.enable_shops', self.enable_shops)
        param.set_param('housing.enable_offices', self.enable_offices)
        param.set_param('housing.enable_transfer', self.enable_transfer)
        param.set_param('housing.enable_portal', self.enable_portal)

    def get_values(self):
        res = super().get_values()
        param = self.env['ir.config_parameter'].sudo()
        res.update(
            enable_residential=param.get_param('housing.enable_residential') == 'True',
            enable_commercial=param.get_param('housing.enable_commercial') == 'True',
            enable_towers=param.get_param('housing.enable_towers') == 'True',
            enable_apartments=param.get_param('housing.enable_apartments') == 'True',
            enable_shops=param.get_param('housing.enable_shops') == 'True',
            enable_offices=param.get_param('housing.enable_offices') == 'True',
            enable_transfer=param.get_param('housing.enable_transfer') == 'True',
            enable_portal=param.get_param('housing.enable_portal') == 'True',
        )
        return res
