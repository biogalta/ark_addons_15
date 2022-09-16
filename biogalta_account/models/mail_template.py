# -*- coding: utf-8 -*-

from odoo import fields, models, api


class MailTemplate(models.Model):
    _inherit = "mail.template"

    email_from = fields.Char('From',
                             help="Sender address (placeholders may be used here). If not set, the default "
                                  "value will be the author's email alias if configured, or email address.",
                             compute='_get_default_email_from', readonly=False)

    def _get_default_email_from(self):
        self.email_from = "${user.email_formatted |safe}"
