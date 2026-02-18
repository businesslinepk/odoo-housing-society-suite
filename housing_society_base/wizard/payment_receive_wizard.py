from odoo import models, fields, api
from odoo.exceptions import UserError


class HousingPaymentReceiveWizard(models.TransientModel):
    _name = "housing.payment.receive.wizard"
    _description = "Receive Installment Payment"

    member_id = fields.Many2one(
        "housing.member",
        string="Member",
        required=True,
        readonly=True
    )

    installment_id = fields.Many2one(
        "housing.installment",
        string="Installment",
        domain="[('member_id','=',member_id),('state','=','pending')]",
        required=True
    )

    amount = fields.Float(string="Amount", required=True)
    payment_date = fields.Date(
        string="Payment Date",
        default=fields.Date.context_today
    )
    payment_method = fields.Selection(
        [
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('easypaisa', 'EasyPaisa'),
            ('jazzcash', 'JazzCash'),
        ],
        default='cash',
        required=True
    )

    def action_confirm_payment(self):
        self.ensure_one()

        if self.amount <= 0:
            raise UserError("Payment amount must be greater than zero.")

        # 1️⃣ Mark installment as PAID
        self.installment_id.write({
            'state': 'paid'
        })

        # 2️⃣ Create ledger entry
        self.env['housing.ledger'].create({
            'member_id': self.member_id.id,
            'date': self.payment_date,
            'description': f'Installment Payment ({self.installment_id.sequence})',
            'credit': self.amount,
            'debit': 0.0,
        })

        return {'type': 'ir.actions.act_window_close'}
