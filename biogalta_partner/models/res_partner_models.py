# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# ADDRESS_FIELDS = ('street', 'street2', 'street_2', 'zip', 'city', 'state_id', 'country_id')


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_promoter = fields.Boolean("Is a promoter",default=False, readonly=True)
    is_commercial = fields.Boolean("Is a commercial",default=False, readonly=True)
    promoter_id = fields.Many2one('res.partner', "Promoter")
    commercial_id = fields.Many2one('res.partner', "Commercial")
    commercial_partner_ids = fields.One2many('res.partner', 'commercial_id', "Customers of commercial")
    promoter_partner_ids = fields.One2many('res.partner', 'promoter_id', "Customers linked")
    is_point_of_sale = fields.Boolean("Is a point of sale", default=False)
    is_prospect = fields.Boolean("Is a prospect", default=False)

    def transform_prospect_to_customer(self):
        partner_ref = self.env['res.partner'].browse(self.id)
        if partner_ref and partner_ref.customer_rank == 0:
            partner_ref.update({
                'customer_rank': 1,
                'is_prospect':False
            })

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self
        name = partner.name or ''

        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
                name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        # if self._context.get('show_vat') and partner.vat:
        #     name = "%s ‒ %s" % (name, partner.vat)
        return name

    @api.model
    def create(self, values):
        res = super(InheritResPartner, self).create(values)
        if 'street' in values:
            res.write({
                'street': values['street']
            })
        if 'street2' in values:
            res.write({
                'street2': values['street2']
            })
        return res

    def action_view_sale_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.act_res_partner_2_sale_order')
        all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        if self.is_company:
            action['domain'] = [('partner_id.commercial_partner_id.id', '=', self.id), ('partner_id', 'in', all_child.ids)]
        else:
            action['domain'] = [('partner_id.id', '=', self.id), ('partner_id', 'in', all_child.ids)]
        return action
