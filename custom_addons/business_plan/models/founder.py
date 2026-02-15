from odoo import api, fields, models


class founder(models.Model):
    _name = 'founder'

    founder_name = fields.Char(string="Nom")
    is_founder = fields.Boolean(string="Est un fondateur")
    business_project_id = fields.Many2one(comodel_name='business.project',inverse_name='founder_ids',string="Projets")
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                 string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda
                                      self: self.env.user.company_id.currency_id.id)
    capital_contribution = fields.Monetary(string="Apport / Capital")
    share_capital = fields.Monetary(string="Apport/Capital du fondateur")
    share_number = fields.Integer(compute="_compute_share_number",string="Nombre d'actions du fondateur")


    @api.depends('share_capital','business_project_id.share_value')
    def _compute_share_number(self):
        for record in self:
            if not record.share_capital == 0 and not record.business_project_id.share_value == 0:
                record.share_number = record.share_capital / record.business_project_id.share_value
            else:
                record.share_number = 0