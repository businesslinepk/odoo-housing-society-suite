from odoo import models, fields, api
from odoo.exceptions import UserError

class HousingTransfer(models.Model):
    _name = "housing.transfer"
    _description = "Plot Transfer"

    plot_id = fields.Many2one("housing.plot", required=True)
    block_id = fields.Many2one(
    "housing.block",
    string="Block",
    related="plot_id.block_id",
   
    readonly=True
)
    from_member_id = fields.Many2one("housing.member", string="From", required=True)
    to_member_id = fields.Many2one("housing.member", string="To", required=True)
    transfer_date = fields.Date(default=fields.Date.today)
    remarks = fields.Text()

    def action_confirm_transfer(self):
        for rec in self:
            if rec.from_member_id == rec.to_member_id:
                raise UserError("From & To member cannot be same")

            # remove plot from old member
            rec.from_member_id.plot_id = False

            # assign plot to new member
            rec.to_member_id.plot_id = rec.plot_id
            rec.to_member_id.status = "active"

            rec.from_member_id.status = "transferred"
    

    def action_print_transfer_allotment(self):
     self.ensure_one()
     return self.env.ref(
        'housing_society_base.action_transfer_allotment_report'
    ).report_action(self)

    @api.onchange("plot_id")
    def _onchange_plot_id(self):
        if self.plot_id:
            self.block_id = self.plot_id.block_id
        else:
            self.block_id = False