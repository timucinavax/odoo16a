{
    'name': 'GDSG Material',
    'version': '1.0',
    'license': 'LGPL-3',
    'description': 'GDSG Material',
    'author': 'son.truong',
    'depends': ['openeducat_timetable'],
    'data': [
        'security/ir.model.access.csv',
        'views/gdsg_material_management_view.xml',
        'views/gdsg_material_transaction_view.xml',
        'views/op_session_inherit_view.xml',
        'views/gdsg_material_bom_view.xml',
        'menus/gdsg_material_menu.xml',
    ],
    'sequence': 1,
    'application': False,
    'installable': True
}
