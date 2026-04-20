from odoo import fields, models


class InterventionDeplacement(models.Model):
    _name = "intervention.deplacement"
    _description = "Déplacement d'intervention"
    _order = "date_deplacement desc"

    name = fields.Char(string="Objet", required=True, default="Déplacement")
    date_deplacement = fields.Datetime(string="Date", required=True)
    location = fields.Char(string="Lieu")
    status = fields.Selection(
        [
            ("planned", "Planifié"),
            ("done", "Réalisé"),
            ("cancel", "Annulé"),
        ],
        string="Statut",
        default="planned",
    )
    task_id = fields.Many2one("project.task", string="Réclamation", required=True, ondelete="cascade")


class InterventionAction(models.Model):
    _name = "intervention.action"
    _description = "Action de réparation"
    _order = "date_action desc"

    name = fields.Char(string="Objet", required=True, default="Action")
    date_action = fields.Datetime(string="Date", required=True)
    description = fields.Text(string="Description")
    technicien_id = fields.Many2one("hr.employee", string="Technicien")
    duree = fields.Float(string="Durée (heures)")
    task_id = fields.Many2one("project.task", string="Réclamation", required=True, ondelete="cascade")
