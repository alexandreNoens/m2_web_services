# Miamzy API

API REST de livraison de repas realisee avec FastAPI et PostgreSQL. Le projet
couvre les cinq besoins suivants :

- lister les commandes avec une pagination par curseur ;
- consulter une commande ;
- creer une commande dans un restaurant ;
- payer une commande avec une cle d'idempotence ;
- consulter le profil public d'un utilisateur.

Le contrat de l'API se trouve dans [`openapi.yml`](openapi.yml). Toutes les
routes sont versionnees sous `/v1`, les prix sont exprimes en centimes d'euro et
les dates utilisent le format RFC 3339.

## Technologies

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL 16 dans Docker
- Uvicorn

## Prerequis

- Python 3.11 ou une version compatible
- Docker avec Docker Compose
- `curl`, `make` et `jq` pour rejouer les preuves

## Installation

Creer l'environnement Python et installer les dependances :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Demarrer PostgreSQL :

```bash
docker compose up -d postgres
```

Initialiser la base avec 20 restaurants et 5 000 commandes :

```bash
.venv/bin/python -m app.seed
```

Le seed est rejouable. Il remet la base dans un etat de demonstration connu et
affiche les identifiants utilisables pour les appels de test.

## Lancement

```bash
.venv/bin/uvicorn app.main:app --reload
```

L'API est alors disponible sur `http://localhost:8000` et sa documentation
interactive sur `http://localhost:8000/docs`.

## Tester les routes

Les commandes de verification de l'etape 1 sont regroupees dans un `Makefile` :

```bash
make -C preuves/etape_1 help
make -C preuves/etape_1 check
make -C preuves/etape_1 list-orders
make -C preuves/etape_1 get-order
make -C preuves/etape_1 create-order
make -C preuves/etape_1 pay-order
make -C preuves/etape_1 get-profile
```

Les captures et les sorties textuelles correspondantes sont disponibles dans
[`preuves/etape_1`](preuves/etape_1/README.md).

Les trois scenarios d'erreur de l'etape 2 peuvent etre verifies avec :

```bash
make -C preuves/etape_2 check
make -C preuves/etape_2 missing-order
make -C preuves/etape_2 empty-cart
make -C preuves/etape_2 invalid-json
```

Les emplacements des captures correspondantes sont prepares dans
[`preuves/etape_2`](preuves/etape_2/README.md).

La pagination bornee et la lecture d'une page suivante de l'etape 3 se verifient avec :

```bash
make -C preuves/etape_3 check
make -C preuves/etape_3 default-page
make -C preuves/etape_3 next-page
make -C preuves/etape_3 oversized-page
make -C preuves/etape_3 explain
```

La requete SQL, son plan d'execution et la procedure de capture sont documentes
dans [`preuves/etape_3`](preuves/etape_3/README.md).

## Arret

Arreter le serveur Uvicorn avec `Ctrl+C`, puis PostgreSQL avec :

```bash
docker compose down
```
