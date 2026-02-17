from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_amount_provision_line = fields.Boolean(compute='_compute_is_amount_provision_line',string="Est la ligne qui gère les montants déjà facturés en guise de provision")

    def _compute_is_amount_provision_line(self):
        """
        Vérifie si le product_id de la ligne de commande
        appartient au product.template défini par l'external ID.
        """
        # Récupère le product.template via son external ID
        # Format : 'nom_du_module.xml_id'
        target_template = self.env.ref('sale_provision_prestation.montants_provision')

        for line in self:
            if not line.product_id:
                continue

            # product_id est un product.product
            # product_id.product_tmpl_id remonte au product.template
            if line.product_id.product_tmpl_id == target_template:
                # ✅ La ligne correspond au bon template
                line.is_amount_provision_line = True
            else:
                # ❌ Pas le bon template
                line.is_amount_provision_line = False


