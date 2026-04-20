# -*- coding: utf-8 -*-

import base64
from odoo import http
from odoo.http import request


class ReclamationController(http.Controller):
    """
    Website Controller for public complaint submission.
    
    This controller provides:
    - A public form for citizens/companies to submit complaints
    - CSRF-protected form submission
    - Automatic complaint creation with proper defaults
    """

    @http.route('/reclamation', type='http', auth="public", website=True)
    def reclamation_form(self, **kwargs):
        """
        Display the complaint submission form.
        Accessible by anyone (public).
        """
        return request.render("AlMiyahDZ.reclamation_form_template", {})

    @http.route('/reclamation/submit', type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def reclamation_submit(self, **post):
        """
        Process the complaint form submission.
        
        Creates a new complaint (project.task with is_claim=True) from the form data.
        Uses sudo() to bypass access rights for public users.
        """
        # Prepare values from the HTML form
        claimant_name = post.get('name') or "Réclamant anonyme"
        email = post.get('email')
        phone = post.get('phone')

        # Find or create partner
        partner = False
        if email:
            partner = request.env["res.partner"].sudo().search([("email", "=", email)], limit=1)

        if not partner:
            partner = request.env["res.partner"].sudo().create({
                "name": claimant_name,
                "email": email,
                "phone": phone,
                "customer_rank": 1,
            })

        # Get project
        project = request.env.ref('AlMiyahDZ.project_project_claim', raise_if_not_found=False)
        if not project:
            project = request.env['project.project'].sudo().search([], limit=1)

        # Map reclamant_type to claim_origin
        reclamant_type = post.get('reclamant_type', 'citoyen')
        claim_origin = 'citizen' if reclamant_type == 'citoyen' else 'company'

        vals = {
            'name': post.get('subject'),  # Objet de la réclamation
            'description': post.get('description'),
            'is_claim': True,  # Force complaint type
            'claim_origin': claim_origin,  # citizen/company
            'type_reclamation': post.get('type_reclamation', 'technical'),
            'claimant_id': partner.id,
            'partner_id': partner.id,
            'project_id': project.id if project else False,
            'agency_id': request.env.ref('AlMiyahDZ.agency_default').id,
            'claimant_address': post.get('address'),
            'claimant_commune': post.get('commune'),
            'claimant_company_name': post.get('company_name') if claim_origin == 'company' else False,
        }

        # Create the complaint with admin rights (sudo) to avoid access errors
        reclamation = request.env['project.task'].sudo().create(vals)

        # Set claim_reference
        reclamation.claim_reference = 'REC-' + str(reclamation.id).zfill(6)

        # Handle attachments
        attachments = request.httprequest.files.getlist("attachment")
        for upload in attachments:
            if upload.filename and upload.content_length > 0:
                data = upload.read()
                if data:
                    request.env["ir.attachment"].sudo().create({
                        "name": upload.filename,
                        "datas": base64.b64encode(data).decode(),
                        "res_model": "project.task",
                        "res_id": reclamation.id,
                        "type": "binary",
                    })

        # Render success page with reference number
        return request.render("AlMiyahDZ.reclamation_success_template", {
            'reclamation': reclamation
        })

    # Public status check
    @http.route('/reclamation/status', type='http', auth="public", website=True, methods=['GET', 'POST'])
    def reclamation_status(self, **post):
        if request.httprequest.method == 'POST':
            reference = post.get('reference')
            email = post.get('email')
            if reference and email:
                task = request.env['project.task'].sudo().search([
                    ('claim_reference', '=', reference),
                    ('is_claim', '=', True),
                    ('partner_id.email', '=', email)
                ], limit=1)
                if task:
                    return request.render("AlMiyahDZ.reclamation_status_template", {'reclamation': task})
                else:
                    return request.render("AlMiyahDZ.reclamation_status_template", {
                        'error': 'Réclamation non trouvée. Vérifiez la référence et l\'email.'
                    })
        return request.render("AlMiyahDZ.reclamation_status_template", {})

    # Portal routes for logged-in users to follow their reclamations
    @http.route("/my/reclamations", type="http", auth="user", website=True)
    def my_claims(self, **kwargs):
        tasks = request.env["project.task"].search([
            ("is_claim", "=", True),
            ("partner_id", "=", request.env.user.partner_id.commercial_partner_id.id),
        ])
        return request.render("AlMiyahDZ.portal_my_claims", {"tasks": tasks})

    @http.route("/my/reclamations/<int:task_id>", type="http", auth="user", website=True)
    def claim_detail(self, task_id, **kwargs):
        task = request.env["project.task"].search([
            ("id", "=", task_id),
            ("is_claim", "=", True),
            ("partner_id", "child_of", [request.env.user.partner_id.commercial_partner_id.id]),
        ], limit=1)
        if not task:
            return request.not_found()
        return request.render("AlMiyahDZ.portal_my_claim_detail", {"task": task})