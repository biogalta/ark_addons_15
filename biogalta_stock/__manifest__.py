# -*- coding: utf-8 -*-
{
    'name': "BIOGalta STOCK",
    'icon': '/biogalta_stock/static/description/icon.png',
    'sequence': -8,
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'Arkeup',
    'website': 'www.arkeup.com',

    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'stock_account', 'product', 'base_import','mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_cost_history_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
