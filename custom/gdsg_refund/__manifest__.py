{
    'name': 'GDSG Refund',
    'version': '1.0',
    'license': 'LGPL-3',
    'description': 'GDSG Refund',
    'author': 'son.truong',
    'depends': ['gdsg_contract','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/gdsg_refund_rule_category_view.xml',
        'views/gdsg_refund_rule_view.xml',
        'views/gdsg_refund_rate_view.xml',
        'views/gdsg_refund_structure_view.xml',
        'views/gdsg_refund_core_view.xml',
        'menus/gdsg_refund_menu.xml',
        'report/report.xml',
    ],
    'sequence': 1,
    'application': False,
    'installable': True
}
