from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_claim = fields.Boolean(string="Réclamation", default=lambda self: self.env.context.get("default_is_claim", False))
    claim_reference = fields.Char(string="Référence", readonly=True, copy=False, index=True)
    claim_origin = fields.Selection(
        [
            ("citizen", "Citoyen"),
            ("company", "Entreprise"),
            ("watch", "Cellule de veille"),
        ],
        string="Origine",
        default="citizen",
        tracking=True,
    )
    claimant_id = fields.Many2one(
        "res.partner",
        string="Réclamant",
        tracking=True,
        domain=[("type", "!=", "delivery")],
    )
    claimant_address = fields.Char(string="Adresse", tracking=True)
    claimant_commune = fields.Char(string="Commune", tracking=True)
    claimant_company_name = fields.Char(string="Raison sociale", tracking=True)
    etat_final = fields.Selection(
        [
            ("resolved", "Résolue"),
            ("rejected", "Rejetée"),
            ("pending", "En attente"),
        ],
        string="État final",
        tracking=True,
    )
    agency_id = fields.Many2one(
        "res.partner",
        string="Agence",
        domain=[("is_agency", "=", True)],
        tracking=True,
    )
    type_reclamation = fields.Selection(
        [
            ("technical", "Technique"),
            ("commercial", "Commerciale"),
        ],
        string="Type de réclamation",
        default="technical",
        tracking=True,
    )
    agent_clientele_id = fields.Many2one("hr.employee", string="Agent clientèle", tracking=True)
    technician_ids = fields.Many2many(
        "hr.employee",
        "task_technician_rel",
        "task_id",
        "employee_id",
        string="Techniciens",
        tracking=True,
    )
    chef_equipe_id = fields.Many2one("hr.employee", string="Chef d'équipe", tracking=True)
    commission_member_ids = fields.Many2many(
        "hr.employee",
        "task_commission_rel",
        "task_id",
        "employee_id",
        string="Commission commerciale",
        tracking=True,
    )
    pv_decision = fields.Html(string="PV / Décision")
    pv_signataires_ids = fields.Many2many(
        "hr.employee",
        "task_pv_signataire_rel",
        "task_id",
        "employee_id",
        string="Signataires PV",
    )
    validation_comptable = fields.Boolean(string="Validation comptable", tracking=True)
    montant_dedommagement = fields.Float(string="Montant dédommagement")
    diagnostic_technique = fields.Html(string="Diagnostic technique")
    complexite = fields.Selection(
        [
            ("faible", "Faible"),
            ("moyenne", "Moyenne"),
            ("elevee", "Élevée"),
            ("critique", "Critique"),
        ],
        string="Complexité",
        default="faible",
    )
    gravite = fields.Selection(
        [
            ("faible", "Faible"),
            ("moyenne", "Moyenne"),
            ("elevee", "Élevée"),
            ("critique", "Critique"),
        ],
        string="Gravité",
        default="faible",
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Facture rectificative",
        domain=[("move_type", "in", ["out_invoice", "out_refund"])],
        readonly=True,
        copy=False,
    )
    deplacement_ids = fields.One2many("intervention.deplacement", "task_id", string="Déplacements")
    action_ids = fields.One2many("intervention.action", "task_id", string="Actions de réparation")
    @api.onchange('type_reclamation')
    def _onchange_type_reclamation(self):
        # Auto-assign basic team based on type (can be customized)
        if self.type_reclamation == 'commercial':
            # Assign default commercial agent if available
            pass  # Placeholder for auto-assignment logic
        elif self.type_reclamation == 'technical':
            # Assign default technician if available
            pass  # Placeholder for auto-assignment logic

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("is_claim") and not vals.get("claim_reference"):
                vals["claim_reference"] = self.env["ir.sequence"].next_by_code("project.task.reclamation")
            if vals.get("claimant_id") and not vals.get("partner_id"):
                vals["partner_id"] = vals.get("claimant_id")
        tasks = super().create(vals_list)
        return tasks

    def action_generate_invoice(self):
        for task in self:
            if not task.claimant_id:
                raise ValidationError(_("Le réclamant est requis pour générer une facture."))
            if task.invoice_id:
                continue
            move_vals = {
                "move_type": "out_invoice",
                "partner_id": task.claimant_id.id,
                "invoice_date": fields.Date.context_today(self),
                "claim_id": task.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": task.name or "Réclamation",
                            "quantity": 1.0,
                            "price_unit": task.montant_dedommagement or 0.0,
                        },
                    )
                ],
            }
            invoice = self.env["account.move"].create(move_vals)
            task.invoice_id = invoice.id
        return True

    def write(self, vals):
        return super().write(vals)

    def action_close_claim(self):
        self.write({"active": False})
        return True
