# Journal de decisions — Groupe : Alexandre Noens

## Etape 0

### 1. Quel langage, quel framework, quelle base ? Pourquoi ceux-la pour une API de cette taille ?

- Langage: Python
- Framework: FastAPI
- Base de donnees: PostgreSQL

Pourquoi ce choix pour une API de taille petite/moyenne (5 besoins):
- FastAPI est rapide a mettre en place et genere la documentation OpenAPI automatiquement.
- Validation des donnees integree (Pydantic), utile pour eviter des erreurs d'entree.
- Python + FastAPI est tres adapte pour livrer vite un contrat clair et testable.
- PostgreSQL est robuste, simple a exploiter pour les commandes/paiements et scalable sans complexite inutile.

Alternatives ecartees:
- Microservices: trop complexe pour 5 routes principales.
- NoSQL: moins pertinent ici car les donnees sont relationnelles (utilisateur, commande, restaurant, paiement).

### 2. Quelles sont vos ressources, et quelles routes pour les 5 besoins du sujet ?

Ressources principales:
- orders
- payments
- users
- restaurants (portee de creation de commande)

Routes retenues:
- Lister les commandes: GET /v1/orders
- Consulter une commande: GET /v1/orders/{orderId}
- Creer une commande dans un restaurant: POST /v1/restaurants/{restaurantId}/orders
- Payer une commande: POST /v1/orders/{orderId}/payments
- Consulter le profil d'un utilisateur: GET /v1/users/{userId}/profile

### 3. Que renvoie chaque route quand tout va bien ? Et quand ca se passe mal ?

Regle generale:
- Succes: codes 2xx + JSON metier
- Erreur: code HTTP adapte + corps application/problem+json

Par route:
- GET /v1/orders
  - OK: 200 avec { data: [...], nextCursor }
  - Erreurs: 400 (parametres invalides), 500 (erreur serveur)

- GET /v1/orders/{orderId}
  - OK: 200 avec la commande complete
  - Erreurs: 404 (commande introuvable), 500

- POST /v1/restaurants/{restaurantId}/orders
  - OK: 201 avec la commande creee
  - Erreurs: 400 (payload invalide), 404 (restaurant/utilisateur introuvable), 409 (conflit metier), 500

- POST /v1/orders/{orderId}/payments
  - OK: 201 avec le paiement cree
  - Erreurs: 400 (payload invalide), 404 (commande introuvable), 409 (deja payee / etat incompatible), 422 (paiement refuse), 500

- GET /v1/users/{userId}/profile
  - OK: 200 avec le profil utilisateur non sensible
  - Erreurs: 404 (utilisateur introuvable), 500

Convention de formats:
- Prix: amountCents (entier), currency = EUR
- Dates: date-time RFC 3339 (ex: 2026-11-20T14:30:00Z)
