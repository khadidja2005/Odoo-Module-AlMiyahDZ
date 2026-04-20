from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_claimant = fields.Boolean(string="Réclamant", default=False)
    is_agency = fields.Boolean(string="Agence AlMiyah", default=False)
    claim_ids = fields.One2many("project.task", "claimant_id", string="Réclamations", domain=[("is_claim", "=", True)])
    claim_count = fields.Integer(string="Nombre de réclamations", compute="_compute_claim_count")

    @api.depends("claim_ids")
    def _compute_claim_count(self):
        for partner in self:
            partner.claim_count = len(partner.claim_ids)

    def action_view_claims(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Réclamations",
            "res_model": "project.task",
            "view_mode": "list,form",
            "domain": [("claimant_id", "=", self.id), ("is_claim", "=", True)],
            "context": {"default_claimant_id": self.id, "default_is_claim": True},
        }


class AccountMove(models.Model):
    _inherit = "account.move"

    claim_id = fields.Many2one(
        "project.task",
        string="Réclamation liée",
        domain=[("is_claim", "=", True)],
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    assigned_claim_ids = fields.Many2many(
        "project.task",
        "task_technician_rel",
        "employee_id",
        "task_id",
        string="Réclamations assignées",
    )
    agency_id = fields.Many2one(
        "res.partner",
        string="Agence",
        domain=[("is_agency", "=", True)],
        help="Agence d'affectation pour limiter l'accès aux réclamations et interventions.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign first agency to new employees in AlMiyahDZ groups."""
        employees = super().create(vals_list)
        employees._auto_assign_agency()
        return employees

    def _auto_assign_agency(self):
        """Assign the first available agency to employees without one."""
        almiyah_groups = self.env['res.groups'].search([
            ('category_id', '=', self.env.ref('AlMiyahDZ.module_category_al_miyahdz').id)
        ])
        first_agency = self.env['res.partner'].search([('is_agency', '=', True)], limit=1, order='id asc')
        if not first_agency:
            return
        for employee in self:
            if employee.agency_id:
                continue
            # Check if employee's user is in any AlMiyahDZ group
            if employee.user_id and any(group in employee.user_id.groups_id for group in almiyah_groups):
                employee.agency_id = first_agency.id


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign agency when user is created with AlMiyahDZ groups."""
        users = super().create(vals_list)
        users._auto_assign_employee_agency()
        return users

    def write(self, vals):
        """Auto-assign agency when user is added to AlMiyahDZ groups."""
        res = super().write(vals)
        if 'groups_id' in vals:
            self._auto_assign_employee_agency()
        return res

    def _auto_assign_employee_agency(self):
        """Assign the first available agency to the employee of users in AlMiyahDZ groups."""
        almiyah_groups = self.env['res.groups'].search([
            ('category_id', '=', self.env.ref('AlMiyahDZ.module_category_al_miyahdz').id)
        ])
        first_agency = self.env['res.partner'].search([('is_agency', '=', True)], limit=1, order='id asc')
        if not first_agency:
            return
        for user in self:
            if not any(group in user.groups_id for group in almiyah_groups):
                continue
            employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
            if employee and not employee.agency_id:
                employee.sudo().agency_id = first_agency.id
