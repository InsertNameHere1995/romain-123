from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    #is_provision_invoice= fields.Boolean(compute="_compute_is_provision_invoice",string="Est une facture de provision")

