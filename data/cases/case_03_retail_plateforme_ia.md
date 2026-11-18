# Cas Client Deloitte #03 : Plateforme IA Générative & Recherche Documentaire (Retail / Grande Distribution)

- **ID Interne :** CASE-RET-2025-021
- **Niveau d'accès IAM :** `All`
- **Secteur :** Retail & Biens de Consommation
- **Client (anonymisé) :** Groupe de Distribution Européen (45 000 collaborateurs)
- **Année :** 2025
- **Durée :** 3 mois

## Contexte & Défi
Déployer une plateforme d'IA générative sécurisée (RAG + Multi-agents) permettant à 3 000 collaborateurs d'interroger des documents internes hétérogènes sans fuite de données et avec une interface accessible (RGAA).

## Solution Déployée par Deloitte
- Architecture serverless sur **Cloud Run** + **Vertex AI Search** + **Gemini**, avec ancrage strict des réponses sur les sources internes (*Grounding*).
- Audit d'accessibilité numérique (**RGAA / WCAG AA**) intégré dès la phase de design UI.

## Résultats Clés (Métriques vérifiées)
- **+4 heures gagnées par semaine** et par collaborateur sur la recherche d'information.
- **Taux d'adoption de 84 %** après 60 jours.
- **Score d'accessibilité RGAA de 96 %** validé par un audit indépendant.
