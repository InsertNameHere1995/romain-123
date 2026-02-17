from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    is_prestation = fields.Boolean(string="Est une prestation",default= False, store=True)
    is_provision = fields.Boolean(string="Est une provision", default=False, store=True)
    sequence_id = fields.Many2one(
        'ir.sequence',
        string='Séquence personnalisée',
        domain="[('code', '=', 'sale.order')]",
        help="Si une séquence est définie ici, elle sera utilisée pour générer "
             "le numéro des bons de commande créés à partir de ce modèle. "
             "Si vide, la séquence par défaut sera utilisée."
    )

    @api.constrains('is_prestation')
    def _check_is_prestation(self):
        for record in self:
            if record.is_prestation and record.is_provision:
                raise ValidationError("_ERROR: You have to chose between Prestation and Provision (or none).")
        # all records passed the test, don't return anything


