{
    'name': 'GDSG Refund',
    'version': '1.0',
    'description': 'GDSG Refund',
    'author': 'son.truong',
    'depends': ['gdsg_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/gdsg_refund_rule_category_view.xml',
        'views/gdsg_refund_rule_view.xml',
        'views/gdsg_refund_rate_view.xml',
        'views/gdsg_refund_structure_view.xml',
        'views/gdsg_refund_core_view.xml',
        'menus/gdsg_refund_menu.xml',
    ],
    'sequence': 1,
    'application': False,
    'installable': True
}
