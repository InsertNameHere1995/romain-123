from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Surcharge de la méthode create pour utiliser la séquence du modèle de devis
        si elle est définie.
        """
        for vals in vals_list:
            # Si le nom n'est pas déjà défini ou est le slash par défaut
            if vals.get('name', '/') == '/' or not vals.get('name'):
                # Vérifier si un modèle de devis est sélectionné
                template_id = vals.get('sale_order_template_id')

                if template_id:
                    template = self.env['sale.order.template'].browse(template_id)

                    # Si le modèle a une séquence personnalisée, l'utiliser
                    if template.sequence_id:
                        company_id = vals.get('company_id') or self.env.company.id
                        vals['name'] = template.sequence_id.with_company(company_id).next_by_id()

        return super(SaleOrder, self).create(vals_list)

