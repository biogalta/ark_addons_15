# -*- coding: utf-8 -*-
{
    'name': "BIOGalta SALE",
    'icon': '/biogalta_sale/static/description/icon.png',
    'sequence': -8,
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
    'category': 'Sale',
    'version': '15.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base', 'sale', 'account', 'stock', 
        'product', 'account_intrastat', 'account_reports', 
        'web', 'l10n_fr','sale_mrp','mail'],

    'data': [
        # 'views/web_template.xml',
        'security/ir.model.access.csv',
        'views/account_tax_views.xml',
        'views/account_invoice_views.xml',
        'views/account_journal_views.xml',
        'views/invoice_report_template.xml',
        'views/sale_views.xml',
        'views/sale_report_inherit_templates.xml',
        'views/res_config_inherit.xml',
        'views/report_inherit.xml',
        'views/stock_report.xml',
        'data/paperformat_data.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            '/biogalta_sale/static/src/css/**/*',
            '/biogalta_sale/static/src/scss/**/*',
        ],
    },    
}
