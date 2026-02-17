from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # ---------------------------------------------------------------------------
    # Champs
    # ---------------------------------------------------------------------------

    so_prestation = fields.Many2one(
        'sale.order',
        string='Commande de Prestation',
        ondelete='restrict',
        domain=[('is_prestation', '=', True)],
    )

    # One2Many inverse du Many2one so_prestation sur le SO de provision.
    # Permet d'écouter directement les factures des SO de provision via @api.depends.
    provision_order_ids = fields.One2many(
        'sale.order',
        'so_prestation',
        string='Commandes de Provision',
    )

    is_prestation = fields.Boolean(
        string="Est Prestation",
        compute="_compute_is_prestation",
        store=True,
    )

    is_provision = fields.Boolean(
        string="Est Provision",
        compute="_compute_is_provision",
        store=True,
    )

    provision_invoices = fields.Many2many(
        'account.move',
        'provision_invoices_rel',
        'order_id',
        'account_move_id',
        string='Factures de Provision',
        readonly=True,
        compute='_compute_provision_invoices',
    )

    invoiced_provision_amount = fields.Float(
        string="Montant Facturé Provision",
        compute='_compute_invoiced_provision_amount',
        store=True,
    )

    # ---------------------------------------------------------------------------
    # Contraintes
    # ---------------------------------------------------------------------------

    @api.constrains('so_prestation')
    def _check_is_prestation(self):
        for record in self:
            if record.is_prestation and record.is_provision:
                raise ValidationError(
                    "Vous devez choisir entre Prestation ou Provision (ou aucun des deux)."
                )

    # ---------------------------------------------------------------------------
    # Computes
    # ---------------------------------------------------------------------------

    @api.depends('sale_order_template_id', 'sale_order_template_id.is_prestation')
    def _compute_is_prestation(self):
        for record in self:
            record.is_prestation = bool(record.sale_order_template_id.is_prestation)

    @api.depends('sale_order_template_id', 'sale_order_template_id.is_provision')
    def _compute_is_provision(self):
        for record in self:
            record.is_provision = bool(record.sale_order_template_id.is_provision)

    @api.depends(
        'is_prestation',
        'provision_order_ids',
        'provision_order_ids.invoice_ids',
        'provision_order_ids.invoice_ids.state',
    )
    def _compute_provision_invoices(self):
        """
        Pour chaque SO de prestation, récupère toutes les factures
        des SO de provision liés via le One2Many provision_order_ids.
        """
        for order in self:
            if order.is_prestation:
                order.provision_invoices = order.provision_order_ids.mapped('invoice_ids')
            else:
                order.provision_invoices = False

    @api.depends(
        'is_prestation',
        'provision_order_ids',
        'provision_order_ids.invoice_ids',
        'provision_order_ids.invoice_ids.amount_total_in_currency_signed',
        'provision_order_ids.invoice_ids.state',
    )
    def _compute_invoiced_provision_amount(self):
        """
        Calcule le montant total des factures de provision
        et met à jour la ligne correspondante sur le SO de prestation.
        """
        for order in self:
            if order.is_prestation:
                order.invoiced_provision_amount = -sum(
                    invoice.amount_total_in_currency_signed
                    for invoice in order.provision_order_ids.mapped('invoice_ids')
                )
                order._update_provision_line()
            else:
                order.invoiced_provision_amount = 0.0

    # ---------------------------------------------------------------------------
    # Méthode utilitaire — création/mise à jour de la ligne de provision
    # ---------------------------------------------------------------------------

    def _update_provision_line(self):
        """Crée ou met à jour la ligne de provision sur le SO de prestation."""
        self.ensure_one()
        provision_line = self.order_line.filtered(lambda l: l.is_amount_provision_line)
        if provision_line:
            provision_line.write({'price_unit': self.invoiced_provision_amount})
        elif self.invoiced_provision_amount:
            product = self.env.ref('your_module.your_product_xml_id')
            self.env['sale.order.line'].create({
                'order_id': self.id,
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': self.invoiced_provision_amount,
                'is_amount_provision_line': True,
            })

    # ---------------------------------------------------------------------------
    # Surcharge create
    # ---------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """
        Utilise la séquence du modèle de devis si elle est définie.
        """
        for vals in vals_list:
            if vals.get('name', '/') == '/' or not vals.get('name'):
                template_id = vals.get('sale_order_template_id')
                if template_id:
                    template = self.env['sale.order.template'].browse(template_id)
                    if template.sequence_id:
                        company_id = vals.get('company_id') or self.env.company.id
                        vals['name'] = template.sequence_id.with_company(company_id).next_by_id()

        return super().create(vals_list)