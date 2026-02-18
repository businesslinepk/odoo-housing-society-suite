from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import base64, qrcode
from io import BytesIO


class HousingMember(models.Model):
    _name = "housing.member"
    _description = "Housing Member"
    _rec_name = "membership_no"

    # =========================
    # BASIC
    # =========================
    membership_no = fields.Char(
        string="Membership No",
        readonly=True,
        copy=False,
        default="New"
    )
    name = fields.Char(string="Name", required=True)
    cnic = fields.Char(required=True)
    phone = fields.Char()
    address = fields.Text()

    file_id = fields.Many2one("housing.file", string="Allotted File", required=True)
    plot_id = fields.Many2one("housing.plot", string="Plot (After Allotment)")

    nominee_ids = fields.One2many("housing.nominee", "member_id")
    ledger_ids = fields.One2many(
        "housing.ledger", "member_id", string="Ledger"
    )

    state = fields.Selection(
        [('active', 'Active'), ('cancelled', 'Cancelled')],
        default='active',
        tracking=True
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        help="Linked accounting customer",
        ondelete="restrict"
    )

    plot_type_label = fields.Char(
        compute="_compute_plot_type_label",
        store=False
    )

    is_downpayment = fields.Boolean(
        string="Down Payment",
        default=False
    )
    
    plot_type_label_upper = fields.Char(
    compute="_compute_plot_type_label_upper",
    store=False
    )
    member_image = fields.Image(
    string="Member Photo",
    max_width=1024,
    max_height=1024,
    attachment=True
    )
     
    cnic_front_image = fields.Image(
        string="CNIC Front",
        attachment=True,
        max_width=1024,
        max_height=1024
    )

    cnic_back_image = fields.Image(
        string="CNIC Back",
        attachment=True,
        max_width=1024,
        max_height=1024
    )
    # =========================
    # FINANCE
    # =========================
    total_price = fields.Float()
    down_payment = fields.Float()
    outstanding_balance = fields.Float(
        compute="_compute_outstanding",
        store=True
    )
    booking_amount = fields.Float()

    installment_months = fields.Integer(default=12)

    # =========================
    # PAYMENT PLAN
    # =========================
    payment_plan = fields.Selection(
        [('full', 'Full Payment'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly')],
        default='monthly',
        required=True
    )

    number_of_years = fields.Integer(default=1)

    show_years = fields.Boolean(
        compute="_compute_show_years",
        store=False
    )

    # =========================
    # INSTALLMENTS
    # =========================
    first_installment_date = fields.Date()

    installment_ids = fields.One2many(
        "housing.installment",
        "member_id"
    )

    installments_completed = fields.Boolean(
        compute="_compute_installments_completed",
        store=True
    )

    plot_allotted = fields.Boolean(default=False)

    # =========================
    # QR
    # =========================
    qr_data = fields.Char(compute="_compute_qr_data", store=True)
    qr_image = fields.Binary(compute="_compute_qr_image", store=False)

    # =========================
    # COMPUTES
    # =========================
    @api.depends("total_price", "down_payment")
    def _compute_outstanding(self):
        for rec in self:
            rec.outstanding_balance = (rec.total_price or 0) - (rec.down_payment or 0)

    @api.depends("installment_ids.state")
    def _compute_installments_completed(self):
        for rec in self:
            if not rec.installment_ids:
                rec.installments_completed = False
            else:
                paid = rec.installment_ids.filtered(lambda i: i.state == 'paid')
                rec.installments_completed = len(paid) == len(rec.installment_ids)

            if rec.installments_completed and rec.plot_id:
                rec.plot_allotted = True

    @api.depends("membership_no")
    def _compute_qr_data(self):
        for rec in self:
            rec.qr_data = f"MEMBERSHIP:{rec.membership_no}" if rec.membership_no else False

    @api.depends("qr_data")
    def _compute_qr_image(self):
        for rec in self:
            if rec.qr_data:
                qr = qrcode.make(rec.qr_data)
                buf = BytesIO()
                qr.save(buf, format="PNG")
                rec.qr_image = base64.b64encode(buf.getvalue())
            else:
                rec.qr_image = False

    @api.depends('payment_plan')
    def _compute_show_years(self):
        for rec in self:
            rec.show_years = rec.payment_plan in ('monthly', 'quarterly')
    
    @api.depends("plot_id")
    def _compute_plot_type_label(self):
        for rec in self:
            if rec.plot_id and rec.plot_id.plot_type:
                rec.plot_type_label = rec.plot_id.plot_type
            else:
                rec.plot_type_label = ""
    # =========================
    # INSTALLMENT LOGIC
    # =========================
    def action_generate_installments(self):
        self.ensure_one()

        if not self.total_price:
            raise UserError("Enter Total Price")

        # Remove old installments
        self.installment_ids.unlink()

        # =========================
        # PLOT SALE LEDGER (ONE TIME)
        # =========================
        existing_sale = self.env["housing.ledger"].search([
            ("member_id", "=", self.id),
            ("description", "=", "Plot Sale - Total Price")
        ], limit=1)

        if not existing_sale:
            self.env["housing.ledger"].create({
                "member_id": self.id,
                "date": fields.Date.today(),
                "description": "Plot Sale - Total Price",
                "debit": self.total_price,
                "credit": 0.0,
            })

        # FULL PAYMENT
        if self.payment_plan == 'full':
            self.installments_completed = True
            self.plot_allotted = True
            return

        if not self.first_installment_date:
            raise UserError("Enter First Installment Date")

        total_installments = (
            12 * self.number_of_years
            if self.payment_plan == 'monthly'
            else 4 * self.number_of_years
        )

        base_amount = (self.total_price or 0) - (self.down_payment or 0)
        per_installment = round(base_amount / total_installments, 2)

        gap = 1 if self.payment_plan == 'monthly' else 3

        for i in range(total_installments):
            self.env['housing.installment'].create({
                'member_id': self.id,
                'sequence': i + 1,
                'due_date': self.first_installment_date + relativedelta(months=i * gap),
                'amount': per_installment,
                'state': 'pending',
            })

    # =========================
    # DOWN PAYMENT INVOICE
    # =========================
    def action_create_downpayment_invoice(self):
        self.ensure_one()

        if not self.down_payment or self.down_payment <= 0:
            raise UserError("Down Payment amount missing.")

        if not self.customer_id:
            raise UserError("Customer not linked with this member.")

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.customer_id.id,
            "invoice_date": fields.Date.today(),
            "housing_member_id": self.id,
            "invoice_line_ids": [(0, 0, {
                "name": f"Down Payment - {self.membership_no}",
                "quantity": 1,
                "price_unit": self.down_payment,
            })],
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": move.id,
            "view_mode": "form",
        }

    # =========================
    # PLOT ALLOTMENT LETTER
    # =========================
    def action_open_plot_allotment_letter(self):
        self.ensure_one()

        unpaid = self.installment_ids.filtered(lambda i: i.state != 'paid')
        if unpaid:
            raise UserError("All installments must be paid first.")

        if not self.plot_id:
            raise UserError("Please select a plot first.")

        return {
            "type": "ir.actions.act_window",
            "name": "Plot Allotment Letter",
            "res_model": "housing.member",
            "res_id": self.id,
            "view_mode": "form",
            "view_id": self.env.ref(
                "housing_society_base.view_plot_allotment_letter_form"
            ).id,
            "target": "current",
        }
    
    def _compute_plot_type_label_upper(self):
        for rec in self:
            if rec.plot_type_label:
                rec.plot_type_label_upper = rec.plot_type_label.upper()
            else:
                rec.plot_type_label_upper = ""


    # =========================
    # CREATE
    # =========================
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("membership_no", "New") == "New":
                vals["membership_no"] = self.env["ir.sequence"].next_by_code(
                    "housing.member"
                ) or "SCA-00001"

        members = super().create(vals_list)

        for member in members:
            if not member.customer_id:
                partner = self.env["res.partner"].create({
                    "name": member.name,
                    "phone": member.phone,
                    "street": member.address,
                    "customer_rank": 1,
                })
                member.customer_id = partner.id

        return members


    # =========================
    # REPORT
    # =========================
    def action_print_allotment_letter(self):
        return self.env.ref(
           "housing_society_base.action_final_allotment_letter"
        ).report_action(self)

