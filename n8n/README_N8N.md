# SPARKY — Intégration n8n

## Architecture

```
┌─────────────────┐     HTTP      ┌──────────────────┐
│   n8n           │ ◄──────────── │  FastAPI Backend  │
│  :5678          │ ──────────►   │  :8000            │
└─────────────────┘               └──────────────────┘
         │                                 │
         │ Webhooks                        │ Mistral AI
         │ Cron Jobs                       │ Google DocAI
         │ Email Alerts                    │ SQLite DB
         ▼                                 ▼
   [Notifications]                  [Documents traités]
```

---

## Démarrage rapide

### Option 1 — Docker Compose (recommandé)

```bash
# 1. Créer le fichier .env à la racine du projet
cp .env.example .env
# Remplir MISTRAL_API_KEY et ALERT_EMAIL

# 2. Lancer tout en une commande
docker-compose up -d

# n8n accessible sur : http://localhost:5678
# API SPARKY sur     : http://localhost:8000
```

### Option 2 — n8n en local (sans Docker)

```bash
# Installer n8n
npm install -g n8n

# Lancer n8n
SPARKY_API_URL=http://localhost:8000 ALERT_EMAIL=ton@email.com n8n start

# Accéder à : http://localhost:5678
```

---

## Connexion à n8n

- URL : http://localhost:5678
- Login : **admin**
- Mot de passe : **sparky2026**

---

## Importer les workflows

1. Ouvrir n8n → menu gauche → **Workflows**
2. Cliquer **Import** (en haut à droite)
3. Importer chaque fichier JSON du dossier `n8n/workflows/`

---

## Les 5 Workflows

| Fichier | Nom | Déclencheur | Description |
|---------|-----|-------------|-------------|
| `workflow_1_traitement_document.json` | Traitement Document | Webhook POST | Reçoit un document en base64, appelle `/process`, retourne JSON |
| `workflow_2_notification_email.json` | Notification Email | Webhook POST | Envoie email HTML après traitement d'un document |
| `workflow_3_comparaison_prix.json` | Comparaison Prix | Cron Lun-Ven 8h | Rapport quotidien des prix par fournisseur par email |
| `workflow_4_rapport_quotidien.json` | Rapport Quotidien | Cron Lun-Ven 7h | Stats stock + valeur + économies potentielles par email |
| `workflow_5_alerte_meilleur_prix.json` | Alerte Meilleur Prix | Cron Lundi 9h | Alerte hebdo si un fournisseur propose un meilleur prix |

---

## Configuration SMTP (pour les emails)

Dans n8n → **Credentials** → **New** → **SMTP** :

| Champ | Valeur exemple (Gmail) |
|-------|----------------------|
| Host | smtp.gmail.com |
| Port | 587 |
| User | ton-email@gmail.com |
| Password | mot de passe application |
| SSL/TLS | STARTTLS |

> Pour Gmail : activer "Mots de passe des applications" dans les paramètres Google.

Nommer la credential : **SPARKY SMTP** (nom exact utilisé dans les workflows).

---

## Tester le Workflow 1 (Traitement document)

```bash
# Encoder un PDF en base64
base64 -i mon_document.pdf > doc_b64.txt

# Appeler le webhook n8n
curl -X POST http://localhost:5678/webhook/sparky/process \
  -H "Content-Type: application/json" \
  -d "{
    \"file_content_base64\": \"$(cat doc_b64.txt)\",
    \"filename\": \"facture.pdf\",
    \"mime_type\": \"application/pdf\"
  }"
```

## Tester le Workflow 2 (Notification email)

```bash
curl -X POST http://localhost:5678/webhook/sparky/notify \
  -H "Content-Type: application/json" \
  -d '{
    "type_document": "facture",
    "fournisseur": "SOTUDERPV",
    "numero_facture": "FAC-2026-001",
    "montant_ttc": "1250.500",
    "score_confiance": 0.94,
    "lignes": [{"designation": "Panneau 400W"}]
  }'
```

---

## Variables d'environnement

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SPARKY_API_URL` | URL du backend SPARKY | `http://localhost:8000` |
| `ALERT_EMAIL` | Email destinataire des alertes | `admin@sparky.tn` |
| `MISTRAL_API_KEY` | Clé API Mistral AI | `AlSTF...` |

---

## Fonctionnalités couvertes sans modifier le code

| Fonctionnalité SPARKY | Automatisation n8n |
|----------------------|-------------------|
| Scanner un document | W1 : Webhook → `/process` |
| Voir un document traité | W2 : Email notification auto |
| Comparateur des prix | W3 : Rapport quotidien email |
| Tableau de bord | W4 : Stats quotidiennes email |
| Prix fournisseurs | W5 : Alerte hebdo meilleur prix |
