# -*- coding: utf-8 -*-
{
    'name': 'Import Bank Statement Lines from Excel/CSV file',
    'version': '15.0.0.1',
    'summary': 'Apps helps to excel import bank statement line import bank statement lines from Excel import cash statement import bank statement from CSV Import statement lines import cash register import multiple bank statements import',
    'description': """
        Import Bank Statement Lines from Excel in odoo , Import Bank Statement from Excel in odoo ,Import Bank report from Excel in odoo 
        Import Cash Statement Lines from Excel
        This module allow you to Import Bank Statement Lines from Excel file.
        This module will allow import Bank and Cash Statements from EXCEL.
        This module will allow import Cash Register Statements From Excel.
        Import Bank Statement Lines from CSV
        Import Cash Statement Lines from CSV
        This module allow you to Import Bank Statement Lines from CSV file.
        This module will allow import Bank and Cash Statements from CSV.
        This module will allow import Cash Register Statements from CSV.
        Excel Bank statement import
        CSV bank statement import
        Excel Cash statement import
        CSV cash statement import
        import bulk statement line, import statement lines
        This module use for import bulk bank statement lines from Excel file. Import statement lines from CSV or Excel file.
        Import statements, Import statement line, Bank statement Import, Add Bank statement from Excel.Add Excel Bank statement lines.Add CSV file.Import invoice data. Import excel file
        Import Bank Statement Lines from XLS
        Import Cash Statement Lines from XLS
        This module allow you to Import Bank Statement Lines from XLS file.
        This module will allow import Bank and Cash Statements from XLS.
        This module will allow import Cash Register Statements From XLS.
        odoo xls Bank statement import
        odoo xls Cash statement import
        odoo import multiple bank statements import excel bank statement import multi bank statement import bank statement
        odoo bank statements import multiple bank statements add multiple bank statements import multiple statements
        odoo add multiple statements Import Multiple Bank Statement from Excel/CSV file Import excel mutiple bank statements
        odoo import csv bank statements Import Banking Transactions Importing Bank Statements
        odoo Importing multiple statements Import multiple statements odoo
        odoo Import Bank Statements Import bank transactions import bank transactions

        Importer des lignes de relevé bancaire à partir d'Excel
        Importer des lignes de relevé de caisse à partir d'Excel
        Ce module vous permet d'importer des lignes de relevé bancaire à partir d'un fichier Excel.
        Ce module permettra l'importation des relevés bancaires et de caisse d'EXCEL.
        Ce module permettra d'importer les relevés de caisse d'Excel.
        Importer les lignes de relevé bancaire de CSV
        Importer des lignes de relevé de caisse à partir de CSV
        Ce module vous permet d'importer des lignes de relevé bancaire à partir d'un fichier CSV.
        Ce module permettra l'importation des relevés bancaires et de caisse de CSV.
        Ce module permettra d'importer les relevés de caisse de CSV.
        Importation d'une déclaration Excel Bank
        Importation de relevés bancaires CSV
        Importation d'un extrait de compte Excel
        Importation de relevés de compte CSV
        importer une ligne d'instruction en bloc, importer des lignes d'instructions
        Ce module est utilisé pour l'importation de lignes de relevés bancaires en vrac à partir d'un fichier Excel. Importer des lignes de relevé à partir d'un fichier CSV ou Excel.
        Importer des relevés, Importer une ligne de relevés, Relevé bancaire Importer, Ajouter un relevé bancaire à partir d'Excel.Add Importer des lignes de relevé bancaire. Ajouter un fichier CSV. Importer des données de facturation. Importer un fichier Excel
        Importer les lignes de relevé bancaire de XLS
        Importer des lignes de relevé de caisse de XLS
        Ce module vous permet d'importer des lignes de relevé bancaire à partir du fichier XLS.
        Ce module permettra l'importation des relevés bancaires et de caisse de XLS.
        Ce module permettra d'importer des relevés de caisse depuis XLS.
        Importation de relevés bancaires xls
        xls Importation de relevés de compte
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','account'],
    'data': [
        "security/ir.model.access.csv",
        "views/bank_statement.xml",
        ],
    'qweb': [
        'static/src/xml/account_reconciliation.xml'
        ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],  
    'license': 'AGPL-3',  
}
