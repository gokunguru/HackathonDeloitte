# Référentiel RSE & Durabilité Deloitte (Pour l'Agent Auditeur RSE)

## 1. Engagements Internes Deloitte (WorldClimate)
- **Trajectoire Net Zero :** Objectifs validés **SBTi** (Science Based Targets initiative) avec réduction de 70 % des émissions opérationnelles et 100 % d'électricité renouvelable dans les bureaux d'ici 2030.
- **Éthique & Inclusion :** Politique active de parité et de diversité dans la composition des équipes projet (minimum 40 % de mixité visée sur les comités de pilotage).
- **Accessibilité Numérique :** Engagement systématique sur les standards **RGAA / WCAG 2.1 AA** pour les interfaces utilisateurs livrées.

## 2. Recommandations Green Cloud (Partenariat Google Cloud)
- **Choix de région bas carbone :** Privilégier `europe-west9` (Paris, mix électrique nucléaire/renouvelable très bas carbone) ou `europe-west1` (Belgique) pour tout hébergement européen.
- **Mesure Scope 3 :** Activer **Google Cloud Carbon Footprint** dès le jour 1 pour fournir un reporting mensuel compatible **CSRD**.
- **FinOps & Éco-conception :** Utiliser des architectures serverless (**Cloud Run** scale-to-zero), le partitionnement **BigQuery** et des modèles **Gemini Flash** (plus sobres en énergie) pour les tâches de routage/classification.
