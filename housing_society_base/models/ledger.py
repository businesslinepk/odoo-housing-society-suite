from odoo import models, fields, api


class HousingLedger(models.Model):
    _name = "housing.ledger"
    _description = "Housing Member Ledger"
    _order = "date, id"

    member_id = fields.Many2one(
        "housing.member",
        string="Member",
        required=True,
        ondelete="cascade"
    )

    invoice_id = fields.Many2one(
    "account.move",
    string="Invoice",
    ondelete="set null"
    )

    date = fields.Date(
        default=fields.Date.context_today,
        required=True
    )

    description = fields.Char(required=True)

    debit = fields.Float(default=0.0)
    credit = fields.Float(default=0.0)

    balance = fields.Float(
        compute="_compute_balance",
        store=True
    )

    #  SAFE BALANCE COMPUTE
    @api.depends("debit", "credit", "member_id")
    def _compute_balance(self):
     for line in self:
        if not line.member_id:
            line.balance = 0.0
            continue

        ledger_lines = self.search(
            [("member_id", "=", line.member_id.id)],
            order="date, id"
        )

        running = 0.0
        for l in ledger_lines:
            running += l.debit - l.credit
            if l.id == line.id:
                line.balance = running
                break
        else:
            #  SAFETY: agar current line mili hi nahi
            line.balance = running

