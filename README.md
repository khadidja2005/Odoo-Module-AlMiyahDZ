# Odoo Module : AlMiyahDZ - Gestion des Réclamations et Interventions

**AlMiyahDZ** est un module Odoo personnalisé conçu pour gérer les interventions, le suivi des réclamations via le portail web, et l'intégration avec la gestion de projets et de tâches.

## 🌟 Fonctionnalités Principales

- **Gestion des Réclamations (Website & Portal) :**
  - Soumission de réclamations directement via le site web (`website_claim.py`).
  - Séquençage automatique des réclamations (`claim_sequence.xml`).
  - Vues dédiées sur le portail client (`portal_templates.xml`).
- **Gestion des Interventions :**
  - Modèles et vues spécifiques pour planifier et suivre les interventions (`intervention_models.py`, `intervention_views.xml`).
- **Suivi des Tâches et Projets :**
  - Héritage et personnalisation des tâches de projets Odoo (`project_task.py`, `project_task_views.xml`).
- **Sécurité et Contrôle d'Accès :**
  - Règles de sécurité personnalisées et gestion stricte des droits d'accès (`security.xml`, `ir.model.access.csv`).

## 📁 Structure du Module

- `controllers/` : Contrôleurs pour les routes web et portail (Ex: `website_claim.py`).
- `data/` : Fichiers de données initiales (Ex: séquences XML).
- `models/` : Définition des modèles de données et héritage des modèles existants (`inhereted_models.py`, `intervention_models.py`).
- `security/` : Fichiers de configuration des groupes d'utilisateurs et droits d'accès.
- `views/` : Vues backend (formulaires, listes, menus) et templates frontend pour le portail.

## 🚀 Installation

1. Placez le dossier `AlMiyahDZ` dans le répertoire `addons` de votre instance Odoo.
2. Redémarrez le service de votre serveur Odoo.
3. Connectez-vous à Odoo en tant qu'administrateur et activez le **Mode Développeur**.
4. Allez dans le menu **Applications**, puis cliquez sur **Mise à jour de la liste des applications**.
5. Cherchez le module **AlMiyahDZ** et cliquez sur **Activer/Installer**.

## 🛠️ Dépendances Techniques
Assurez-vous que les modules Odoo dont dépend `AlMiyahDZ` (comme `website`, `project`, `portal`) sont bien mentionnés dans le fichier `__manifest__.py` et installés sur votre base de données.

## 📝 Licence
Consultez le fichier `LICENSE` inclus pour plus de détails. 
