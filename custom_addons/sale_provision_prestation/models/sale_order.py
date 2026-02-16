from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    so_prestation = fields.Many2one(
        'sale.order',  # comodel_name: Le nom technique du modèle cible (ici, le modèle des contacts)
        string='Commande de Prestation',  # string: Le libellé affiché dans l'interface utilisateur
        ondelete='restrict',  # ondelete: Définit le comportement en cas de suppression de l'enregistrement lié
        domain=[('is_prestation', '=', True)]
        )
    is_prestation= fields.Boolean(string="Est Prestation",compute="_compute_is_prestation")
    is_provision = fields.Boolean(string="Est Provision", compute="_compute_is_provision")



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

    @api.constrains('sale_order_template_id')
    def _compute_is_provision(self):
        for record in self:
            if record.sale_order_template_id.is_provision:
                record.is_provision = True
            else:
                record.is_provision = False

    @api.constrains('sale_order_template_id')
    def _compute_is_prestation(self):
        for record in self:
            if record.sale_order_template_id.is_prestation:
                record.is_prestation = True
            else:
                record.is_prestation = False