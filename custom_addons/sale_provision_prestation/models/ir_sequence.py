from odoo import models, fields, api


class IrSequence(models.Model):
    _inherit= "ir.sequence"

    #client_reference_as_suffix= fields.Boolean(string="Is the suffix based on the client's ref?")