from odoo import models, fields, api
from odoo.exceptions import UserError


class HousingInstallment(models.Model):
    _name = "housing.installment"
    _description = "Housing Installment"
    _order = "sequence asc"

    installment_no = fields.Char(
        string="Installment No",
        readonly=True,
        copy=False,
        default="New"
    )

    is_downpayment = fields.Boolean(
    string="Down Payment",
    default=False
    )

    member_id = fields.Many2one(
        "housing.member",
        string="Member",
        required=True,
        ondelete="cascade"
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=False
    )

    name = fields.Char(
        string="Installment No",
        readonly=True
    )

    sequence = fields.Integer(string="Installment #")

    due_date = fields.Date(
        string="Due Date",
        required=True
    )

    amount = fields.Float(
        string="Amount",
        required=True
    )

    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        ondelete="set null"
    )

    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("paid", "Paid"),
        ],
        string="Status",
        default="pending",
        required=True
    )

    # =========================
    # CREATE
    # =========================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("installment_no", "New") == "New":
                vals["installment_no"] = self.env["ir.sequence"].next_by_code(
                    "housing.installment"
                ) or "INST-0001"

            if vals.get("member_id"):
                count = self.search_count([
                    ("member_id", "=", vals["member_id"])
                ])
                vals["sequence"] = count + 1
                vals["name"] = str(vals["sequence"])

            return super().create(vals)

    # =========================
    # CREATE INVOICE
    # =========================
    def action_create_invoice(self):
     self.ensure_one()

     partner = self.member_id.customer_id
     if not partner:
        raise UserError("Please assign a Customer to this Member first.")

     move = self.env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": partner.id,
        "invoice_date": fields.Date.today(),
        "housing_installment_id": self.id,  #  MOST IMPORTANT
        "invoice_line_ids": [(0, 0, {
            "name": f"Housing Installment #{self.sequence}",
            "quantity": 1,
            "price_unit": self.amount,
        })],
     })

     self.invoice_id = move.id
 
     return {
        "type": "ir.actions.act_window",
        "res_model": "account.move",
        "res_id": move.id,
        "view_mode": "form",
    }

    # =========================
    # MARK AS PAID
    # =========================
    def action_mark_paid(self):
        for rec in self:
            if rec.state == "paid":
                continue

            self.env["housing.ledger"].create({
                "member_id": rec.member_id.id,
                "date": fields.Date.today(),
                "description": f"Installment #{rec.sequence} Paid",
                "debit": 0.0,
                "credit": rec.amount,
            })

            rec.state = "paid"

            
    def _mark_paid_from_invoice(self):
     for rec in self:
        if rec.state == "paid":
            return

        # Ledger entry
        #self.env["housing.ledger"].create({
            #"member_id": rec.member_id.id,
            #"date": fields.Date.today(),
           # "description": f"Installment #{rec.sequence} Paid via Invoice",
            #"debit": 0.0,
            #"credit": rec.amount,
        #})
        # 🔹 LEDGER ENTRY (INSTALLMENT DUE)
        self.env["housing.ledger"].create({
           "member_id": self.member_id.id,
            "date": fields.Date.today(),
            "description": f"Installment #{self.sequence} Due",
            "debit": self.amount,
            "credit": 0.0,
        })

        rec.state = "paid"
