from odoo import models, fields
from odoo.exceptions import UserError

class HousingRefundWizard(models.TransientModel):
    _name = "housing.refund.wizard"
    _description = "Refund Wizard"

    member_id = fields.Many2one(
        "housing.member",
        required=True,
        readonly=True
    )

    refund_amount = fields.Float(required=True)
    reason = fields.Char(required=True)

    def action_confirm_refund(self):
        self.ensure_one()

        if self.refund_amount <= 0:
            raise UserError("Refund amount must be greater than zero.")

        # Ledger DEBIT entry
        self.env["housing.ledger"].create({
            "member_id": self.member_id.id,
            "description": f"Refund: {self.reason}",
            "debit": self.refund_amount,
            "credit": 0.0,
        })

        return {"type": "ir.actions.act_window_close"}
