# SPARKY

Plateforme web d'intelligence documentaire pour le secteur photovoltaïque tunisien. Scanne, classifie et extrait automatiquement les données de factures, devis, bons de livraison, bons de commande et avoirs grâce à Mistral AI, avec persistance PostgreSQL, authentification sécurisée, export Google Sheets et notifications email orchestrées via n8n.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend | Angular 17 (Signals, Material, RxJS) |
| Backend | FastAPI + Python 3.12 |
| Base de données | PostgreSQL 18 |
| ORM | SQLAlchemy async + asyncpg |
| IA | Mistral AI (`mistral-small-latest` + `pixtral-12b-2409`) |
| Workflow | n8n (notifications email + export Google Sheets) |
| Authentification | bcrypt (passlib) + PostgreSQL |
| Hashing | bcrypt 4.0.1 |
| Export | openpyxl (Excel) + Google Sheets API |

> **Version v2 disponible** : `Sparky_v2` upgradé en **Angular 20.3** + Material 20 (Material 3) + Node 24 LTS. Voir section `Migration v2` plus bas.

---

## Fonctionnalités

- **Scan multi-format** : PDF, JPG, PNG, TIFF
- **Classification automatique IA** : facture / devis / bon de livraison / bon de commande / avoir
- **Extraction structurée** : fournisseur, n° document, dates, montants HT/TVA/TTC, lignes articles
- **Score de confiance IA** affiché sur chaque document
- **Comparaison de prix** entre fournisseurs avec mise en évidence du moins cher
- **Catalogue stock** : articles + mouvements (entrées / sorties / inventaires / retours)
- **Export Excel** mis en forme et **Google Sheets** automatique (1 ligne par article extrait)
- **Notification email HTML** détaillée à chaque scan via n8n (tableau articles, totaux, bouton sheet)
- **Authentification sécurisée** (bcrypt, PostgreSQL `users`)
- **Tableau de bord** avec totaux par type, score IA, fournisseur, montant TTC
- **Persistance hybride** : PostgreSQL (source de vérité) + localStorage (cache navigateur)

---

## Installation

### 1. Prérequis

- **Python 3.12+**
- **Node.js 18+** (ou Node 22+ pour la v2)
- **PostgreSQL 18** (utilisateur `sparky`, base `sparky_db`)
- **n8n** (`npm install -g n8n`)

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install "bcrypt==4.0.1" email-validator
```

Crée `backend/.env` :
```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DATABASE_URL=postgresql+asyncpg://sparky:sparky_pass@127.0.0.1:5432/sparky_db
MISTRAL_API_KEY=<ta_cle_mistral>
MISTRAL_MODEL=mistral-small-latest
MISTRAL_VISION_MODEL=pixtral-12b-2409
N8N_WEBHOOK_URL=http://localhost:5678/webhook/sparky/notify
N8N_WEBHOOK_SECRET=sparky-secret
ALLOWED_ORIGINS=["http://localhost:4200","http://localhost:3000"]
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

Crée un admin (génère le hash bcrypt avec `python -c "from passlib.hash import bcrypt; print(bcrypt.hash('motdepasse'))"`):

```sql
INSERT INTO users (email, password_hash, nom, role)
VALUES ('admin@sparky.tn', '<hash_bcrypt>', 'Admin', 'admin');
```

### 4. Frontend

```bash
cd frontend
npm install
```

### 5. n8n (workflow IA)

Importe le workflow :
1. Lance `n8n start` → http://localhost:5678
2. Workflows → Import from file → `n8n/workflows/sparky_pipeline_ia_complet.json`
3. Configure les credentials : Google Sheets OAuth2 + SMTP Gmail
4. Active le workflow

### 6. Démarrage complet

Double-clic sur `start-all.bat` à la racine — démarre backend (8000), frontend (4200) et n8n (5678) dans 3 fenêtres distinctes.

---

## Utilisation

1. Ouvre http://localhost:4200
2. **Connexion** : email + mot de passe (compte créé en DB)
3. **Scanner** un document via la page Scanner (caméra ou upload de fichier)
4. Le document est automatiquement :
   - Classifié + extrait par Mistral AI (~3s)
   - Sauvegardé en PostgreSQL (table `documents` + table spécifique au type)
   - Notifié à n8n via webhook → email HTML + ajout au Google Sheet
5. Visualise le résultat dans le **Tableau de bord** ou **Documents**
6. Compare les prix multi-fournisseurs via **Comparateur**
7. Consulte les niveaux de stock dans **Catalogue**

---

## Architecture

```
   ┌─────────────────────┐
   │  Frontend Angular   │ ← localStorage (cache)
   │  http://localhost:4200
   └────────┬────────────┘
            │ POST /process
            ▼
   ┌─────────────────────┐
   │  FastAPI Backend    │
   │  http://localhost:8000
   └────┬───────┬───────┬┘
        │       │       │
        ▼       ▼       ▼
   ┌─────────┐ ┌────────────┐ ┌───────────────┐
   │Mistral AI│ │PostgreSQL │ │  n8n webhook  │
   │ Vision   │ │ sparky_db │ │   (5678)      │
   │ + Text   │ └────────────┘ └──┬──────┬─────┘
   └─────────┘                    │      │
                                  ▼      ▼
                         ┌──────────────┐ ┌────────────────┐
                         │ Google Sheets│ │  Email HTML    │
                         │   (export)   │ │  (Gmail SMTP)  │
                         └──────────────┘ └────────────────┘
```

---

## Endpoints API

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/auth/login` | Connexion (vérifie hash bcrypt) |
| POST | `/auth/register` | Création utilisateur |
| POST | `/process` | Pipeline complet (upload + classify + extract + DB + n8n) |
| POST | `/upload` | Upload seul (sans IA) |
| POST | `/classify` | Classification Mistral |
| POST | `/extract` | Extraction Mistral |
| POST | `/compare` | Comparaison de prix |
| POST | `/export/excel` | Export Excel d'une liste d'articles |
| GET | `/documents?limit=N` | Liste documents extraits (DB) |
| POST | `/articles/normalize` | Normalisation d'une ligne (catalogue) |
| POST | `/articles/import` | Import lignes d'un document → stock |
| GET | `/articles/stock` | Catalogue stock complet |
| GET | `/articles/comparaison-prix` | Comparateur fournisseurs |
| GET | `/health` | Healthcheck |

---

## Structure du projet

```
Sparky/
├── backend/                      FastAPI + services IA
│   ├── main.py                   Endpoints + auth + pipeline /process
│   ├── config.py                 Settings (Pydantic)
│   ├── database.py               Engine SQLAlchemy async
│   ├── orm_models.py             Modèles ORM (Fournisseur, Document, Facture…)
│   ├── services/                 Classifier, Extractor, Comparator, Normalizer, articles_db
│   ├── requirements.txt
│   └── .env                      Configuration (gitignored si possible)
├── frontend/                     Angular 17
│   └── src/app/
│       ├── pages/                login, home, scanner, documents, comparison, catalogue
│       ├── services/             api.service, document.service, auth.service
│       ├── components/           navbar
│       └── models/               document.model, …
├── database/
│   └── schema.sql                Schéma PostgreSQL (16 tables + enums)
├── n8n/
│   └── workflows/
│       └── sparky_pipeline_ia_complet.json     Workflow 11 nodes
├── start-all.bat                 Lance backend + frontend + n8n
├── README.md
└── RAPPORT_SPARKY.txt            Rapport projet
```

---

## Pipeline n8n (11 nodes)

À chaque scan, le backend POST le webhook n8n. Le workflow exécute :

1. **Réception Document** (webhook entrée)
2. **Validation et Détection Type** (PDF / image)
3. **Classification IA** (label, confiance, niveau)
4. **Résultat Classification**
5. **Extraction Données IA** (lignes, totaux)
6. **Résultat Extraction**
7. **Préparation lignes Google Sheet** (1 row par article)
8. **Export Google Sheet** (append rows)
9. **Construction Email HTML** (header, infos, tableau articles, bouton sheet)
10. **Envoi Email** SMTP
11. **Réponse Finale** (JSON acknowledgement)

---

## Schéma DB principal (PostgreSQL)

| Table | Rôle |
|-------|------|
| `users` | Authentification (bcrypt) |
| `fournisseurs` | Annuaire des fournisseurs |
| `documents` | Table maître (tous types confondus) |
| `factures`, `devis`, `bons_commande`, `bons_livraison`, `avoirs` | Données par type |
| `lignes_facture`, `lignes_devis`, `lignes_bl` | Détail des articles |
| `articles` | Catalogue normalisé (référence interne, spécifications JSONB) |
| `articles_fournisseurs` | Prix achat / vente par fournisseur |
| `mouvements_stock` | Entrées/sorties (stock = `SUM(quantite)`) |

Types ENUM : `document_type`, `document_status`, `mouvement_type`.

---

## Migration v2 — Angular 20

Une version `Sparky_v2` est disponible avec :

| Package | v1 | v2 |
|---------|-----|-----|
| Angular | 17.3 | **20.3** |
| Material | 17.3 | **20.2** (Material 3) |
| TypeScript | 5.4 | **5.8** |
| Node | 18+ | **24 LTS** |

Modifications appliquées :
- `standalone: false` ajouté à tous les composants déclarés dans NgModule
- `styles.scss` réécrit avec la nouvelle API `mat.theme()` (Material 3)
- Cascade `ng update 18 → 19 → 20`

---

## Auteur

**Mahmoud Elloumi** — Étudiant ingénieur en informatique
mahmoud.elloumi@enis.tn
Année universitaire : 2025-2026
