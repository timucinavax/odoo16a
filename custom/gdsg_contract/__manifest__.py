{
    'name': 'GDSG Contract',
    'version': '1.0',
    'license': 'LGPL-3',
    'description': 'GDSG Contract',
    'author': 'son.truong',
    'depends': [],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/gdsg_contract_core_view.xml',
        'views/gdsg_contract_transaction_revenue_view.xml',
        'views/gdsg_contract_transaction_expense_view.xml',
        'menus/gdsg_contract_menu.xml',
    ],
    'sequence': 1,
    'application': False,
    'installable': True
}
