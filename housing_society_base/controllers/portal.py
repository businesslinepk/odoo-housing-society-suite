from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class HousingPortal(CustomerPortal):

    @http.route(['/my/ledger'], type='http', auth='user', website=True)
    def portal_my_ledger(self, **kw):

        partner = request.env.user.partner_id

        member = request.env['housing.member'].sudo().search([
            ('customer_id', '=', partner.id)
        ], limit=1)

        ledger_lines = request.env['housing.ledger'].sudo().search(
            [('member_id', '=', member.id)],
            order='date'
        ) if member else []

        return request.render(
            'housing_society_base.portal_my_ledger_template',
            {
                'ledger_lines': ledger_lines,
                'member': member,
            }
        )
