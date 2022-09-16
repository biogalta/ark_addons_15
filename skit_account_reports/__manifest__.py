# -*- coding: utf-8 -*-
{
    'name': "Odoo Financial Reports in PDF",
    'version': '0.1',
    'summary': 'This module helps to generate Financial reports Balance Sheet, Profit and Loss, Trial Balance, General Ledger, Partner Ledger and Aged Partner Balance in PDF format',
    'author': 'Srikesh Infotech',
    'description': """
        Long description of module's purpose
    """,
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'description': """
        This module helps to generate Financial reports Balance Sheet, Profit and Loss, Trial Balance, General Ledger, Partner Ledger and Aged Partner Balance in PDF format
        """,
    'images': ['images/main_screenshot.png'],
    'category': "Accounting",
    'depends': ['account','skit_financial_form'],
    'data': [
        'wizard/account_report_trial_balance_view.xml',        
        'views/account_menuitem.xml',
        'views/account_report.xml',
        'wizard/account_financial_report_view.xml',
        'views/report_trialbalance.xml',
        'wizard/account_report_general_ledger_view.xml',
        'views/report_generalledger.xml',
        'wizard/account_financial_report_view.xml',
        'views/report_financial.xml',
        'wizard/account_report_aged_partner_balance_view.xml',        
        'views/report_agedpartnerbalance.xml',
        'wizard/account_report_partner_ledger_view.xml',        
        'views/report_partnerledger.xml',
        'wizard/account_report_print_journal_view.xml',
        'views/report_journal.xml',
        'views/report_tax.xml',
    ],
    'installable': True,    
    'auto_install': False,
    'application': True,
}
