# Cas Client Deloitte #01 : Migration Data & IA Souveraine (Banque Européenne)

- **ID Interne :** CASE-FIN-2025-014
- **Niveau d'accès IAM :** `Consulting_Banque`, `Manager`, `Partner`
- **Secteur :** Banque & Services Financiers
- **Client (anonymisé) :** Grande Banque de Détail Européenne (Top 5 Zone Euro)
- **Année :** 2025
- **Durée :** 5 mois (MVP livré en 3,5 mois)

## Contexte & Défi
Migration d'un entrepôt de données legacy (Teradata) vers Google Cloud (BigQuery + Vertex AI) dans un cadre réglementaire strict (**DORA** et **RGPD**), avec un objectif d'hébergement 100 % européen (`europe-west9` Paris).

## Solution Déployée par Deloitte
- Mise en place d'un Data Lakehouse sécurisé sur BigQuery avec cloisonnement IAM granulaire et Cloud DLP pour l'anonymisation des données clients.
- Déploiement de 2 cas d'usage GenAI sur Vertex AI (zéro rétention, zéro ré-entraînement) pour 1 200 conseillers bancaires.
- Formation et acculturation de 35 ingénieurs internes via une Data Academy dédiée.

## Résultats Clés (Métriques vérifiées)
- **-40 %** de coûts d'infrastructure Data dès la première année.
- **100 %** de conformité validée lors de l'audit DORA préliminaire.
- **MVP livré en 14 semaines** grâce aux accélérateurs Terraform Deloitte.
