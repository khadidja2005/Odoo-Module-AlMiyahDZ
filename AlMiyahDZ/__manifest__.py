{
    "name": "AlMiyahDZ - Gestion des Réclamations",
    "version": "18.0.1.0.0",
    "author": "Akal Ahlem & Brakta Khadidja",
    "license": "LGPL-3",
    "summary": "Gestion des réclamations pour AlMiyah Djazair",
    "description": """
Module de gestion des réclamations pour l'entreprise AlMiyah Djazair.
=====================================================================

Ce module permet de:
* Recenser les réclamations (citoyens, entreprises, cellule de veille)
* Traiter les réclamations techniques et commerciales
* Gérer les interventions et déplacements
* Suivre les diagnostics et actions de réparation
* Générer des factures rectificatives
* Offrir un portail client pour le suivi des réclamations
    """,
    "category": "Services",
    "depends": [
        "base",
        "contacts",
        "project",
        "hr",
        "mail",
        "website",
        "portal",
        "calendar",
        "account",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/claim_sequence.xml",
        "views/project_task_views.xml",
        "views/intervention_views.xml",
        "views/inhereted_views.xml",
        "views/portal_templates.xml",
        "views/menus.xml",
    ],
    "controllers": [  # 👈 ADD THIS SECTION
        "controllers/website_claim.py",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
