# SPARKY

Plateforme web d'intelligence documentaire pour le secteur photovoltaïque. Scanne, classifie et extrait automatiquement les données de factures, devis, bons de livraison, bons de commande et avoirs grâce à Mistral AI.

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | Angular 17 (Signals, Material) |
| Backend | FastAPI + Python 3.12 |
| Base de données | PostgreSQL 18 |
| ORM | SQLAlchemy async + asyncpg |
| IA | Mistral AI (`mistral-small-latest` + `pixtral-12b-2409`) |
| Workflow | n8n (notifications email + export Google Sheets) |
| Authentification | bcrypt + PostgreSQL |

## Fonctionnalités

- **Scan multi-format** : PDF, JPG, PNG, TIFF
- **Classification automatique** : facture / devis / bon de livraison / bon de commande / avoir
- **Extraction structurée** : fournisseur, n° document, dates, montants HT/TVA/TTC, lignes articles
- **Comparaison de prix** entre fournisseurs
- **Catalogue stock** : articles + mouvements (entrées / sorties)
- **Export Excel + Google Sheets** automatique
- **Notification email HTML** détaillée à chaque scan via n8n
- **Authentification** sécurisée (bcrypt, PostgreSQL)
- **Tableau de bord** avec totaux par type, score de confiance IA

## Installation

### 1. Prérequis

- Python 3.12+
- Node.js 18+
- PostgreSQL 18 (`sparky_db` + utilisateur `sparky`)
- n8n (`npm install -g n8n`)

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Configure `backend/.env` :

```
DATABASE_URL=postgresql+asyncpg://sparky:sparky_pass@127.0.0.1:5432/sparky_db
MISTRAL_API_KEY=<ta_cle>
N8N_WEBHOOK_URL=http://localhost:5678/webhook/sparky/notify
```

### 3. Base de données

Dans pgAdmin ou psql :

```sql
\i database/schema.sql
```

Crée la table `users` pour l'authentification :

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nom           VARCHAR(255),
    role          VARCHAR(50) DEFAULT 'user',
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
```

### 4. Frontend

```bash
cd frontend
npm install
```

### 5. Démarrage complet

Double-clic sur `start-all.bat` à la racine — démarre backend (8000), frontend (4200) et n8n (5678).

## Utilisation

1. Ouvre http://localhost:4200
2. Connecte-toi (crée d'abord un user via `/auth/register` ou directement en DB avec un hash bcrypt)
3. Scanne un document via la page **Scanner** (caméra ou upload)
4. Le document est automatiquement :
   - Classifié + extrait par Mistral AI
   - Sauvegardé en PostgreSQL
   - Envoyé par email via n8n avec un tableau HTML
   - Exporté vers Google Sheets (1 ligne par article)
5. Visualise le résultat dans le **Tableau de bord** ou **Documents**

## Architecture

```
[Frontend Angular] -> POST /process -> [FastAPI Backend]
                                            |
                                      [Mistral AI]
                                            |
                                      [PostgreSQL]
                                            |
                                      [Webhook n8n]
                                            |
                        +-------------------+-------------------+
                        |                   |                   |
                  [Google Sheets]      [Email HTML]          [Logs]
```

## Endpoints API principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/auth/login` | Connexion (bcrypt) |
| POST | `/auth/register` | Création utilisateur |
| POST | `/process` | Pipeline complet (upload + classify + extract + DB + n8n) |
| POST | `/upload` | Upload seul |
| POST | `/classify` | Classification Mistral |
| POST | `/extract` | Extraction Mistral |
| POST | `/compare` | Comparaison prix |
| POST | `/export/excel` | Export Excel |
| GET | `/documents?limit=N` | Liste documents extraits |
| GET | `/articles/stock` | Catalogue stock |
| GET | `/articles/comparaison-prix` | Comparateur fournisseurs |
| GET | `/health` | Healthcheck |

## Structure du projet

```
Sparky/
├── backend/              FastAPI + services IA
│   ├── main.py           Endpoints + auth + pipeline /process
│   ├── config.py         Settings (Pydantic)
│   ├── database.py       Engine SQLAlchemy async
│   ├── orm_models.py     Modèles ORM
│   ├── services/         Classifier, Extractor, Comparator, Normalizer
│   └── requirements.txt
├── frontend/             Angular 17
│   └── src/app/
│       ├── pages/        login, home, scanner, documents, ...
│       └── services/     api.service, document.service, auth.service
├── database/
│   └── schema.sql        Schéma PostgreSQL complet (16 tables + enums)
├── n8n/
│   └── workflows/
│       └── sparky_pipeline_ia_complet.json    Workflow n8n
├── start-all.bat         Lance backend + frontend + n8n
└── README.md
```

## Pipeline n8n

À chaque scan, le backend envoie un POST au webhook n8n. Le workflow exécute :

1. **Réception** du document scanné
2. **Validation** + détection format (PDF / image)
3. **Classification IA** (Mistral)
4. **Extraction IA** (Mistral)
5. **Préparation lignes** Google Sheet
6. **Export Google Sheets** (1 ligne par article extrait)
7. **Construction email HTML** (tableau articles + bouton lien sheet)
8. **Envoi email** SMTP

## Schéma DB principal

- `users` — authentification
- `fournisseurs` — annuaire fournisseurs
- `documents` — table maître (tous types confondus)
- `factures`, `devis`, `bons_commande`, `bons_livraison`, `avoirs` — données par type
- `lignes_facture`, `lignes_devis`, `lignes_bl` — détail des articles
- `articles` — catalogue normalisé
- `articles_fournisseurs` — prix achat / vente par fournisseur
- `mouvements_stock` — entrées/sorties (le stock = `SUM(quantite)`)

## Auteur

**Mahmoud Elloumi** — Étudiant ingénieur en informatique
mahmoud.elloumi@enis.tn
