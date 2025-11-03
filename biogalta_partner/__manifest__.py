# -*- coding: utf-8 -*-
{
    'name': "BIOGalta PARTNER",
    'sequence': -9,
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'Arkeup',
    'website': 'www.arkeup.com',

    'category': 'Uncategorized',
    'version': '18.0.0.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale', 'sale_management', 'account', 'account_accountant', 'payment',
                'account_reports', 'account_intrastat', 'l10n_fr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_inherit_views.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
}
