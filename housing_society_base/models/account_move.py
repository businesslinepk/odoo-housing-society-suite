from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    housing_installment_id = fields.Many2one(
        "housing.installment",
        string="Housing Installment"
    )

    housing_member_id = fields.Many2one(
        "housing.member",
        string="Housing Member"
    )

    def action_post(self):
        #  Invoice post hone par kuch bhi paid NA karo
        return super().action_post()

    def write(self, vals):
        res = super().write(vals)

        for move in self:
            if move.move_type != "out_invoice" or move.state != "posted":
                continue

            # =========================
            # INSTALLMENT PAYMENT
            # =========================
            installment = self.env["housing.installment"].search([
                ("invoice_id", "=", move.id),
                ("state", "!=", "paid")
            ], limit=1)

            if installment:
                installment.state = "paid"

                self.env["housing.ledger"].create({
                    "member_id": installment.member_id.id,
                    "invoice_id": move.id,
                    "date": move.invoice_date or fields.Date.today(),
                    "description": f"Installment #{installment.sequence} Paid",
                    "debit": 0.0,
                    "credit": installment.amount,   # IMPORTANT
                })

                continue  # ⬅ very important

            # =========================
            # DOWN PAYMENT PAYMENT
            # =========================
            member = self.env["housing.member"].search([
                ("customer_id", "=", move.partner_id.id)
            ], limit=1)

            if member:
                existing = self.env["housing.ledger"].search([
                    ("invoice_id", "=", move.id)
                ], limit=1)

                if not existing:
                    self.env["housing.ledger"].create({
                        "member_id": member.id,
                        "invoice_id": move.id,
                        "date": move.invoice_date or fields.Date.today(),
                        "description": "Down Payment Received",
                        "debit":   0.0, #  DEBIT
                        "credit":  move.amount_total,
                    })

        return res
