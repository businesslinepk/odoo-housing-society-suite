from odoo import http
from odoo.http import request

class MembershipVerify(http.Controller):

    @http.route(
        '/verify/membership/<string:membership_no>',
        type='http',
        auth='public',
        website=True
    )
    def verify_membership(self, membership_no, **kw):

        member = request.env['housing.member'].sudo().search(
            [('membership_no', '=', membership_no)],
            limit=1
        )

       # if not member:
           # return request.render(
               # 'housing_society_base.verify_not_found'
            #)

        return request.render(
            'housing_society_base.verify_membership_page',
            {
                'member': member
            }
        )
