# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from datetime import datetime, timedelta
from odoo import models, api, _, fields
from odoo.tools import float_is_zero


class AccountReportInherit(models.AbstractModel):
    _inherit = 'account.report'

    def open_journal_items(self, options, params):
        """ Get all journal items corresponding to the regroupement 401 and 411 account"""
        action = super(AccountReportInherit, self).open_journal_items(options, params)
        if params and 'id' in params:
            active_id = params['id']
            acc = self.env['account.account'].browse(active_id)

            if acc.code in ('401', '411'):
                action['context'].pop('search_default_account_id')
                accounts = self.env['account.account'].search([('code', '=like', '411%')])
                if acc.code == '401':
                    accounts = self.env['account.account'].search([('code', '=like', '401%')])
                action['domain'].extend([('account_id', 'in', accounts.ids)])
                action['domain'].insert(1, '&')
        return action

    def open_document(self, options, params=None):
        """ FIX error on menu View Journal Entry  : put the right domain  and view"""
        if not params:
            params = {}

        ctx = self.env.context.copy()
        ctx.pop('id', '')

        # Decode params
        model = params.get('model', 'account.move.line')
        res_id = params.get('id')
        document = params.get('object', 'account.move')

        # Redirection data
        if document != "account.move":
            target = self._resolve_caret_option_document(model, res_id, document)
            view_name = self._resolve_caret_option_view(target)
            module = 'account'
            if '.' in view_name:
                module, view_name = view_name.split('.')

            # Redirect
            view_id = self.env['ir.model.data'].get_object_reference(module, view_name)[1]

            res = {
                    'type': 'ir.actions.act_window',
                    'view_type': 'tree',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'res_model': document,
                    'view_id': view_id,
                    'res_id': target.id,
                    'context': ctx,
                }
            return res
        # modif Alice
        else:
            # Alice correction : View journal entry
            acc = self.env['account.account'].browse(res_id)
            date_from = datetime.strptime(options.get('date').get('date_from'), "%Y-%m-%d")
            date_to = datetime.strptime(options.get('date').get('date_to'), "%Y-%m-%d")
            domain_acc = []
            if acc.code in ('401', '411'):
                accounts = self.env['account.account'].search([('code', '=like', '411%')])
                if acc.code == '401':
                    accounts = self.env['account.account'].search([('code', '=like', '401%')])

                domain_acc = self.env[model].search([('account_id', 'in', accounts.ids), ('date', '>=', date_from),
                                                      ('date', '<=', date_to)]).mapped('move_id')
            else:
                domain_acc = self.env[model].search(
                        [('account_id', '=', res_id), ('date', '>=', date_from), ('date', '<=', date_to)]).mapped('move_id')

            action = self.env.ref('account.action_move_journal_line').read()[0]
            ctx = eval(action.get('context'))
            del ctx['search_default_misc_filter']
            #if domain_acc:
            action.update({'domain': [('id', 'in', domain_acc.ids)],
                           'view_id':'account.view_move_tree',
                           'view_type':'list',
                           'context': ctx,'view_mode':"tree,form"})

            return action
        # end Alice

    def open_tax(self, options, params=None):
        res = super(AccountReportInherit, self).open_tax(options, params)
        if res.get('domain', False) and res.get('res_model', False):
            move_lines = self.env[res['res_model']].search(res['domain'])
            add_ids = []
            for line in move_lines:
                for eco_tax in line.tax_ids.filtered(lambda tax: tax.tax_group_id.is_eco_tax):
                    add_ids += line.move_id.line_ids.filtered(lambda line: line.tax_line_id == eco_tax).ids
            if add_ids:
                res['domain'] = ['|', ('id', 'in', add_ids)] + res['domain']
        return res


# TODO: This model needs to be rewritten for Odoo 18's new accounting report architecture.
# The 'account.coa.report' model no longer exists in Odoo 18.
# Temporarily commented out to allow module installation.

# class report_account_coa_global(models.AbstractModel):
#     _name = "account.coa.report.global"
#     _description = "Chart of Account Report"
#     _inherit = "account.coa.report"
#     
#     def _clean_request(self, res, code):
#         res_ids=[];extra_accounts=[]
#         for k in res:
#             if k.code.find(code)==0:
#                 res_ids.append(k.id)
#             else:
#                 extra_accounts.append(k.id)
#         return [res_ids,extra_accounts]
# 
#     @api.model
#     def _get_lines(self, options, line_id=None):
#         # Create new options with 'unfold_all' to compute the initial balances.
#         # Then, the '_do_query' will compute all sums/unaffected earnings/initial balances for all comparisons.
#         new_options = options.copy()
#         new_options['unfold_all'] = True
#         options_list = self._get_options_periods_list(new_options)
#         accounts_results, taxes_results = self.env['account.general.ledger']._do_query(
#             options_list, fetch_lines=False)
# 
#         lines = []
#         totals = [0.0] * (2 * (len(options_list) + 2))
# 
#         # Add lines, one per account.account record.
#         customer_grouped_account_id = self.env['account.account'].search([('code','=','411000000')],limit=1)
#         purchase_grouped_account_id = self.env['account.account'].search([('code','=','401000000')],limit=1)
#         acc411 = self.env['account.account'].search([('code','like','411%')])
#         acc401 = self.env['account.account'].search([('code','like','401%')])
#         acc411_ids=self._clean_request(acc411,'411')[0]
#         acc401_ids=self._clean_request(acc401,'401')[0]
#         extra_accounts411=self._clean_request(acc411,'411')[1]
#         extra_accounts401=self._clean_request(acc401,'401')[1]
# 
#         if len(extra_accounts411)>0:
#             for extra in extra_accounts411:
#                 if extra in acc411_ids:
#                     acc411_ids.remove(extra)
# 
#         if len(extra_accounts401)>0:
#             for extra in extra_accounts401:
#                 if extra in acc401_ids:
#                     acc401_ids.remove(extra)                    
# 
#         sums411=[];account_balance411 = 0.0;initial_balance411_pos=0.0
#         initial_balance411_neg=0.0;total_debit411=0.0;total_credit411=0.0
#         total_balance411_pos=0.0;total_balance411_neg=0.0
#         
#         sums401=[];account_balance401 = 0.0;initial_balance401_pos=0.0
#         initial_balance401_neg=0.0;total_debit401=0.0;total_credit401=0.0
#         total_balance401_pos=0.0;total_balance401_neg=0.0        
#         idx411=0;idx401=0;idx411_inserted=False;idx401_inserted=False;m=0
#         account_balance401_pos=0.0;account_balance401=0.0
#         account_balance411_pos=0.0;account_balance411=0.0
#         final_balance411_neg=0.0;final_balance411_pos=0.0
#         final_balance401_neg=0.0;final_balance401_pos=0.0
#         for account, periods_results in accounts_results:
#             if account.id not in acc411_ids and account.id not in acc401_ids:
#                 sums = []
#                 account_balance = 0.0
#                 for i, period_values in enumerate(reversed(periods_results)):
#                     account_sum = period_values.get('sum', {})
#                     account_un_earn = period_values.get('unaffected_earnings', {})
#                     account_init_bal = period_values.get('initial_balance', {})
# 
#                     if i == 0:
#                         # Append the initial balances.
#                         initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
#                         sums += [
#                             initial_balance > 0 and initial_balance or 0.0,
#                             initial_balance < 0 and -initial_balance or 0.0,
#                         ]
#                         account_balance += initial_balance
# 
#                     # Append the debit/credit columns.
#                     sums += [
#                         account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0),
#                         account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0),
#                     ]
#                     account_balance += sums[-2] - sums[-1]
# 
#                 # Append the totals.
#                 sums += [
#                     account_balance > 0 and account_balance or 0.0,
#                     account_balance < 0 and -account_balance or 0.0,
#                 ]
# 
#                 # account.account report line.
#                 columns = []
#                 for i, value in enumerate(sums):
#                     # Update totals.
#                     totals[i] += value
# 
#                     # Create columns.
#                     columns.append({'name': self.format_value(value, blank_if_zero=True), 
#                         'class': 'number', 'no_format_name': value})
#                 name = account.name_get()[0][1]
#                 lines.append({
#                     'id': self._get_generic_line_id('account.account', account.id),
#                     'name': name,
#                     'title_hover': name,
#                     'columns': columns,
#                     'unfoldable': False,
#                     'caret_options': 'account.account',
#                     'class': 'o_account_searchable_line o_account_coa_column_contrast',
#                 })
#             elif account.id in acc411_ids:
#                 if not idx411_inserted:
#                     idx411=m
#                     lines.append("idx411")
#                     idx411_inserted=True
#                 i=0
#                 for i, period_values in enumerate(reversed(periods_results)):
#                     account_sum = period_values.get('sum', {})
#                     account_un_earn = period_values.get('unaffected_earnings', {})
#                     account_init_bal = period_values.get('initial_balance', {})
#                     final_balance = account_sum.get("balance", 0.0)
#                     if i == 0:
#                         # initial balances.
#                         initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
#                         if str(initial_balance).find('-')==0:
#                             initial_balance411_neg+=abs(initial_balance)
#                         else:
#                             initial_balance411_pos+=initial_balance
#                     if str(final_balance).find('-')==0:
#                         final_balance411_neg+=final_balance
#                     else:
#                         final_balance411_pos+=final_balance
#                     account_balance411+=initial_balance
#                     # debit/credit columns.
#                     total_debit411+=account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0)
#                     total_credit411+=account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0)                        
#             elif account.id in acc401_ids:
#                 if not idx401_inserted:
#                     idx401=m
#                     lines.append("idx401")
#                     idx401_inserted=True
#                 i=0
#                 for i, period_values in enumerate(reversed(periods_results)):
#                     account_sum = period_values.get('sum', {})
#                     account_un_earn = period_values.get('unaffected_earnings', {})
#                     account_init_bal = period_values.get('initial_balance', {})
#                     final_balance = account_sum.get("balance", 0.0)
#                     if i == 0:
#                         # initial balances.
#                         initial_balance = account_init_bal.get('balance', 0.0) + account_un_earn.get('balance', 0.0)
#                         if str(initial_balance).find('-')==0:
#                             initial_balance401_neg+=initial_balance
#                         else:
#                             initial_balance401_pos+=initial_balance
#                     if str(final_balance).find("-")==0:
#                         final_balance401_neg+=final_balance
#                     else:
#                         final_balance401_pos+=final_balance
#                     account_balance401+=initial_balance
# 
#                     # debit/credit columns.
#                     total_debit401+=account_sum.get('debit', 0.0) - account_init_bal.get('debit', 0.0)
#                     total_credit401+=account_sum.get('credit', 0.0) - account_init_bal.get('credit', 0.0)                        
#                     i+=1
#             m+=1
# 
#         #group 411 ------------
#         total_debit_final411 = (initial_balance411_pos-initial_balance411_neg)+(total_debit411-total_credit411)+abs(final_balance411_neg)
#         sums411 = [
#             initial_balance411_pos or 0.0,
#             abs(initial_balance411_neg) or 0.0,
#         ]
#         sums411 += [
#             total_debit411,
#             total_credit411,
#         ]
#         sums411 += [
#             total_debit_final411 or 0.0,
#             abs(final_balance411_neg) or 0.0,
#         ]
#         columns411 = []
#         for i, value in enumerate(sums411):
#             # Create columns.
#             columns411.append({'name': self.format_value(value, blank_if_zero=True), 
#                 'class': 'number', 'no_format_name': value})
#         name411 = customer_grouped_account_id.name_get()[0][1]
#         #group 401 ------------
#         sums401 = [
#             initial_balance401_pos or 0.0,
#             abs(initial_balance401_neg) or 0.0,
#         ]
#         sums401 += [
#             total_debit401,
#             total_credit401,
#         ]                    
#         sums401 += [
#             final_balance401_pos or 0.0,
#             abs(final_balance401_neg) or 0.0,
#         ]
#         columns401 = []
#         for i, value in enumerate(sums401):
#             # Create columns.
#             columns401.append({'name': self.format_value(value, blank_if_zero=True), 
#                 'class': 'number', 'no_format_name': value})
#         name401 = purchase_grouped_account_id.name_get()[0][1]
#         for k, n in enumerate(lines):
#             if n=="idx401":
#                 lines[k]={
#                     'id': self._get_generic_line_id('account.account', purchase_grouped_account_id.id),
#                     'name': name401,
#                     'title_hover': name401,
#                     'columns': columns401,
#                     'unfoldable': False,
#                     'caret_options': 'account.account',
#                     'class': 'o_account_searchable_line o_account_coa_column_contrast',
#                 }
#             elif n=="idx411":
#                 lines[k]={
#                     'id': self._get_generic_line_id('account.account', customer_grouped_account_id.id),
#                     'name': name411,
#                     'title_hover': name411,
#                     'columns': columns411,
#                     'unfoldable': False,
#                     'caret_options': 'account.account',
#                     'class': 'o_account_searchable_line o_account_coa_column_contrast',
#                 }
#         return lines
# 
#     @api.model
#     def _get_report_name(self):
#         return _("Balance Générale Biogalta")
# 
#     def _post_process_grouped(self, grouped_accounts, initial_balances, options, comparison_table):
#         lines = []
#         context = self.env.context
#         company_id = context.get('company_id') or self.env.user.company_id
#         title_index = ''
#         sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
#         zero_value = ''
#         sum_columns = [0, 0, 0, 0]
#         for period in range(len(comparison_table)):
#             sum_columns += [0, 0]
# 
#         temp_customer, temp_supplier, toremove = [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], []
#         for account in sorted_accounts:
#             # skip accounts with all periods = 0 and no initial balance
#             non_zero = False
#             for p in range(len(comparison_table)):
#                 if (grouped_accounts[account][p]['debit'] or grouped_accounts[account][p]['credit']) or \
#                         not company_id.currency_id.is_zero(initial_balances.get(account, 0)):
#                     non_zero = True
#             if not non_zero:
#                 continue
# 
#             initial_balance = initial_balances.get(account, 0.0)
#             sum_columns[0] += initial_balance if initial_balance > 0 else 0
#             sum_columns[1] += -initial_balance if initial_balance < 0 else 0
#             cols = [
#                 {'name': initial_balance > 0 and self.format_value(initial_balance) or zero_value,
#                  'no_format_name': initial_balance > 0 and initial_balance or 0},
#                 {'name': initial_balance < 0 and self.format_value(-initial_balance) or zero_value,
#                  'no_format_name': initial_balance < 0 and abs(initial_balance) or 0, 'style': 'padding-right: 35px'},
#             ]
#             total_periods = 0
#             for period in range(len(comparison_table)):
#                 amount = grouped_accounts[account][period]['balance']
#                 debit = grouped_accounts[account][period]['debit']
#                 credit = grouped_accounts[account][period]['credit']
#                 total_periods += amount
#                 cols += [{'name': debit > 0 and self.format_value(debit) or zero_value,
#                           'no_format_name': debit > 0 and debit or 0},
#                          {'name': credit > 0 and self.format_value(credit) or zero_value,
#                           'no_format_name': credit > 0 and abs(credit) or 0, 'style': 'padding-right: 35px'}]
#                 # In sum_columns, the first 2 elements are the initial balance's Debit and Credit
#                 # index of the credit of previous column generally is:
#                 p_indice = period * 2 + 1
#                 sum_columns[(p_indice) + 1] += debit if debit > 0 else 0
#                 sum_columns[(p_indice) + 2] += credit if credit > 0 else 0
# 
#             total_amount = initial_balance + total_periods
#             sum_columns[-2] += total_amount if total_amount > 0 else 0
#             sum_columns[-1] += -total_amount if total_amount < 0 else 0
#             cols += [
#                 {'name': total_amount > 0 and self.format_value(total_amount) or zero_value,
#                  'no_format_name': total_amount > 0 and total_amount or 0},
#                 {'name': total_amount < 0 and self.format_value(-total_amount) or zero_value,
#                  'no_format_name': total_amount < 0 and abs(total_amount) or 0},
#             ]
#             name = account.code + " " + account.name
#             line = {
#                 'id': account.id,
#                 'name': len(name) > 40 and not context.get('print_mode') and name[:40] + '...' or name,
#                 'title_hover': name,
#                 'columns': cols,
#                 'unfoldable': False,
#                 'caret_options': 'account.account'}
#             lines.append(line)
# 
#             # ALICE
# 
#             # for line in lines:
#             if name[:3] in ("411", "401"):
#                 temp = temp_supplier
#                 account_global = self.env['account.account'].search([('code', '=', '401')])
#                 if name[:3] == "411":
#                     temp = temp_customer
#                 temp[0] = cols[0]['no_format_name'] + temp[0]
#                 temp[1] = cols[1]['no_format_name'] + temp[1]
#                 temp[2] = cols[2]['no_format_name'] + temp[2]
#                 temp[3] = cols[3]['no_format_name'] + temp[3]
#                 temp[4] = cols[4]['no_format_name'] + temp[4]
#                 temp[5] = cols[5]['no_format_name'] + temp[5]
#                 toremove.append(line)
# 
#         for t in toremove: lines.remove(t)
# 
#         if temp_customer:
#             acc_customer = self.env.ref('biogalta_account.fr_pcg_recv_grouped_')
#             if acc_customer:
#                 grouped_customer = self.create_grouped_line(acc_customer, temp_customer)
#                 if grouped_customer:
#                     lines.append(grouped_customer)
#         if temp_supplier:
#             acc_supplier = self.env.ref('biogalta_account.fr_pcg_pay_grouped_')
#             if acc_supplier:
#                 supplier_grouped_line = self.create_grouped_line(acc_supplier, [t * -1 for t in temp_supplier])
#                 if supplier_grouped_line:
#                     lines.append(supplier_grouped_line)
# 
#         if lines:
#             lines = sorted(lines, key=lambda l: l.get('name'))
# 
#         # END ALICE
#         lines.append({
#             'id': 'grouped_accounts_total',
#             'name': _('Total'),
#             'class': 'total',
#             'columns': [{'name': self.format_value(v)} for v in sum_columns],
#             'level': 1,
#         })
#         return lines
# 
#     def create_grouped_line(self, account_global, temp_lines):
#         zero_value = ''
# 
#         name = account_global.code + " " + account_global.name
#         cols = [
#             {'name': temp_lines[0] > 0 and self.format_value(temp_lines[0]) or zero_value,
#              'no_format_name': temp_lines[0] > 0 and temp_lines[0] or 0},
#             {'name': temp_lines[1] < 0 and self.format_value(-temp_lines[1]) or zero_value,
#              'no_format_name': temp_lines[1] < 0 and abs(temp_lines[1]) or 0,
#              'style': 'padding-right: 35px'},
#             {'name': temp_lines[2] > 0 and self.format_value(temp_lines[2]) or zero_value,
#              'no_format_name': temp_lines[2] > 0 and temp_lines[2] or 0},
#             {'name': temp_lines[3] > 0 and self.format_value(temp_lines[3]) or zero_value,
#              'no_format_name': temp_lines[3] > 0 and abs(temp_lines[3]) or 0, 'style': 'padding-right: 35px'},
#             {'name': temp_lines[4] > 0 and self.format_value(temp_lines[4]) or zero_value,
#              'no_format_name': temp_lines[4] > 0 and temp_lines[4] or 0},
#             {'name': temp_lines[5] < 0 and self.format_value(-temp_lines[5]) or zero_value,
#              'no_format_name': temp_lines[5] < 0 and abs(temp_lines[5]) or 0}
#         ]
#         for i,t in enumerate(temp_lines):
#             if temp_lines[i] != 0:
#                 return ({'id': account_global.id,
#                  'name': len(name) > 40 and not self.env.context.get('print_mode') and name[:40] + '...' or name,
#                  'title_hover': name,
#                  'columns': cols,
#                  'unfoldable': False,
#                  'caret_options': 'account.account'
#                  })
#         return False
