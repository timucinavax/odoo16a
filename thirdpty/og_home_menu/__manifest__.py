# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'og_home_menu',
    'author': 'VnSoft',
    'maintainer': 'Odoog',
    'support': 'vnsoft.he@gmail.com',
    'website': 'https://www.odoog.com',
    'description': """
App Home Menu display ICON.
""",
    'version': '16.0.1.0.0',
    'sequence': 99,
    'depends': ['web'],
    "excludes": ["web_enterprise"],
    #'data' : ["views/website_templates.xml"],
    'qweb': [],
    'assets': {
        'web.assets_backend': [
            'og_home_menu/static/src/css/appmenu.css',
            'og_home_menu/static/xml/appsmenu.xml',
        ],
        'web.assets_frontend': [
            #'og_home_menu/static/src/css/website_appmenu.css',
        ]
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
