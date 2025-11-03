# -*- coding: utf-8 -*-
{
    'name': "biogalta_account",
    'icon': '/biogalta_account/static/description/icon.png',
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'Arkeup',
    'website': 'www.arkeup.com',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '18.0.0.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','account_reports','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',  # TODO: Uncomment when model is rewritten for Odoo 18
        'views/views.xml',
        # 'data/grouped_account.xml',  # TODO: Rewrite for Odoo 18 (account.account.template no longer exists)
    ],
}