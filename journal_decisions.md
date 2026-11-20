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
- Erreur metier: code HTTP adapte + corps application/problem+json
- Validation des entrees: 422 au meme format application/problem+json que les autres erreurs

Par route:
- GET /v1/orders
  - OK: 200 avec { data: [...], nextCursor }
  - Erreurs: 422 (parametres invalides), 500 (erreur serveur)

- GET /v1/orders/{orderId}
  - OK: 200 avec la commande complete
  - Erreurs: 404 (commande introuvable), 422 (identifiant invalide), 500

- POST /v1/restaurants/{restaurantId}/orders
  - OK: 201 avec la commande creee
  - Erreurs: 404 (restaurant/utilisateur/article introuvable), 409 (restaurant ferme ou article indisponible), 422 (entree invalide), 500
  - Les prix et le montant total sont calcules par le serveur a partir des articles en base.

- POST /v1/orders/{orderId}/payments
  - OK: 201 avec le paiement cree
  - Erreurs: 402 (paiement refuse), 404 (commande introuvable), 409 (cle reutilisee pour une autre requete ou commande annulee), 422 (entree invalide ou cle absente), 500
  - Le client genere une cle d'idempotence et l'envoie dans le header Idempotency-Key.
  - La cle est stockee avec le paiement en base et reste conservee pour toute la duree de l'exercice.
  - La meme requete avec la meme cle renvoie exactement la meme reponse 201, sans creer un autre paiement.
  - Une cle differente correspond a un nouveau paiement, meme si la commande a deja ete payee.

- GET /v1/users/{userId}/profile
  - OK: 200 avec uniquement id, firstName, lastName et createdAt
  - Erreurs: 404 (utilisateur introuvable), 422 (identifiant invalide), 500
  - L'email, le telephone et le mot de passe hache restent en base et ne sont jamais renvoyes.

Convention de formats:
- Prix: tous les champs termines par Cents sont des entiers en centimes d'euro, currency = EUR
- Dates: date-time RFC 3339 (ex: 2026-11-20T14:30:00Z)
