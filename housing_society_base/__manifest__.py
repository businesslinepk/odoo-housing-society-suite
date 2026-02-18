{
    "name": "Housing Society Base",
    "version": "19.0.1.0.0",
    "summary": "Housing Society / Real Estate Base Module",
    "category": "Real Estate",
    "author": "Business Lines Private Limited",
    "depends": ["base", "contacts", "portal", "account"],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",  

        'views/member_action.xml',
        'views/installment_action.xml',

        "views/society_view.xml",
        "views/block_view.xml",
        "views/plot_view.xml",
        "views/member_view.xml",
        "views/transfer_view.xml", 
        "views/ledger_view.xml",
        "views/installment_view.xml",
        "views/allotment_letter_template.xml",
        "views/plot_allotment_view.xml",
        "views/plot_allotment_action.xml",
        "views/report.xml",
        "views/file_view.xml",
        "views/portal_menu.xml",
        "views/portal_ledger.xml",
        "views/refund_wizard_view.xml",
        "views/verify_membership_templates.xml",
        
        "reports/report_action.xml",
        "reports/plot_allotment_report.xml",
        "reports/plot_allotment_letter.xml",
        "reports/transfer_allotment_template.xml",
        "reports/transfer_allotment_report.xml",

        'wizard/payment_receive_wizard.xml',

        "views/menu.xml",
    ],

    'assets': {
    'web.assets_backend': [
        'housing_society_base/static/src/css/print_hide.css',
    ],
}, 
    "installable": True,
    "application": True,
    "license": "OPL-1",
    'price': 110,
    'currency': "USD",
    'images': ['static/description/icon.png'],
}
