# SPARKY — Document Intelligence for Photovoltaïques

Application web angulaire de gestion documentaire intelligente pour la filière photovoltaïque.

## Architecture

```
sparky/
├── frontend/          # Angular 17 — Interface utilisateur
├── backend/           # Python FastAPI — API IA
├── n8n/               # Workflow n8n importable
└── database/          # Schema PostgreSQL
```

## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Angular 17, Angular Material |
| Backend | Python FastAPI, Google Document AI |
| Middleware | n8n (webhooks + workflows) |
| Base de données | PostgreSQL + Supabase Storage |

## 5 catégories de documents

| Type | Description |
|---|---|
| Facture | Facture fournisseur avec lignes |
| Bon de livraison | Bon de livraison avec suivi |
| Bon de commande | Commande fournisseur |
| Avoir | Note de crédit / avoir |
| Devis | Proposition commerciale avec comparaison de prix |

## Fonctionnalités IA

- **Classification** : identification automatique du type + score de confiance
- **Extraction** : données structurées (références, montants, dates, fournisseur)
- **Comparateur de prix** : compare les devis entre fournisseurs, affiche le moins cher

## Démarrage rapide

### 1. Base de données

```bash
psql -U postgres -c "CREATE DATABASE sparky_db;"
psql -U postgres -d sparky_db -f database/schema.sql
```

### 2. Backend FastAPI

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Configurer les variables
uvicorn main:app --reload --port 8000
```

### 3. Frontend Angular

```bash
cd frontend
npm install
ng serve --port 4200
```

Accéder à http://localhost:4200

### 4. n8n Workflow

1. Démarrer n8n : `npx n8n`
2. Ouvrir http://localhost:5678
3. Importer `n8n/workflow.json`
4. Configurer les credentials PostgreSQL
5. Activer le workflow

## API Endpoints

| Méthode | Route | Description |
|---|---|---|
| POST | `/upload` | Téléverser un document |
| POST | `/classify` | Classifier le type de document |
| POST | `/extract` | Extraire les données structurées |
| POST | `/compare` | Comparer les prix des devis |
| POST | `/process` | Tout-en-un : upload + classify + extract |
| GET | `/health` | Vérifier l'état de l'API |

## Variables d'environnement

Copier `backend/.env.example` en `backend/.env` et configurer :

- `DATABASE_URL` : URL PostgreSQL
- `SUPABASE_URL` + `SUPABASE_KEY` : Stockage Supabase
- `GOOGLE_PROJECT_ID` + `GOOGLE_PROCESSOR_ID` : Google Document AI
- `N8N_WEBHOOK_URL` : URL webhook n8n

## Développement

L'API fonctionne en **mode dégradé** sans Google Document AI configuré :
- Classification par mots-clés (heuristique)
- Extraction par expressions régulières
- Stockage local si Supabase non configuré
