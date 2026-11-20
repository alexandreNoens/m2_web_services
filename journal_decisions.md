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

## Etape 1

### 1. Organisation de l'API

- Toutes les routes sont placees sous `/v1` pour rendre la version explicite.
- Les URL decrivent des ressources avec des noms et aucun verbe; l'action est portee par la methode HTTP.
- Le code est une seule application FastAPI, suffisante pour les cinq besoins sans ajouter de microservices.
- SQLAlchemy gere le modele relationnel et PostgreSQL est lance dans Docker; FastAPI reste lance localement pour faciliter le developpement.

### 2. Donnees de demonstration

- Le script `python -m app.seed` genere 20 restaurants, 100 utilisateurs, 100 articles et 5 000 commandes.
- Un generateur pseudo-aleatoire avec une graine fixe et des UUID v5 rend les identifiants reproductibles.
- Le seed remet volontairement les tables a zero afin que chaque demonstration parte du meme etat.
- Certains restaurants sont fermes, certains articles indisponibles et les commandes ont plusieurs statuts pour fournir des donnees realistes.

Alternatives ecartees:
- Faker: dependance inutile pour les quelques champs necessaires a cette etape.
- UUID v4 pour le seed: les identifiants changeraient a chaque lancement et rendraient les commandes curl difficiles a reproduire.
- Base en memoire: elle ne prouverait pas l'utilisation de PostgreSQL et perdrait toutes les donnees au redemarrage.

### 3. Comportements retenus

- La liste est triee de la plus recente a la plus ancienne et utilise un curseur Base64 opaque contenant la date et l'identifiant de la derniere commande.
- Le serveur lit les prix des articles en base et calcule lui-meme le total lors de la creation.
- Les paiements stockent la cle d'idempotence et une empreinte de la requete; meme cle et meme requete renvoient le meme paiement.
- Toutes les erreurs exposees par l'API, y compris les erreurs de validation FastAPI, utilisent `application/problem+json`.
- Les informations sensibles de l'utilisateur existent en base pour verifier qu'elles ne sont pas exposees par la route de profil.

## Etape 2

### Format et codes d'erreur

- Toutes les erreurs utilisent `application/problem+json` et les cinq champs `type`, `title`, `status`, `detail` et `instance`, conformement au format Problem Details (RFC 9457).
- Les erreurs metier passent par une exception `ApiProblem`; les erreurs de validation et les erreurs HTTP de FastAPI sont converties par des gestionnaires globaux afin de garantir la meme forme partout.
- Une ressource absente renvoie 404, une entree invalide (dont un panier vide ou du JSON illisible) renvoie 422, et un conflit avec l'etat courant renvoie 409.
- Le champ `detail` indique au client la valeur ou l'etat a corriger, tandis que `instance` identifie la route concernee.

Alternatives ecartees:
- Le corps FastAPI par defaut `{ "detail": ... }`, car il n'a pas la meme forme que les erreurs metier.
- Un code 500 pour une erreur de syntaxe JSON, car la requete du client est invalide et le serveur n'est pas en faute.

## Etape 3

### Regles de pagination

- La liste renvoie 20 commandes par defaut et accepte au maximum 100 commandes.
- Une demande superieure a 100 est refusee avec une erreur `422` plutot que plafonnee silencieusement. Le client sait ainsi que son parametre est invalide.
- La pagination utilise un curseur opaque plutot qu'un numero de page. Son cout ne depend pas du nombre de pages deja parcourues et les insertions recentes ne decaleraient pas les pages suivantes.
- L'ordre est stable : `created_at DESC, id DESC`. L'identifiant departage les commandes qui ont exactement la meme date.
- La requete lit `limit + 1` lignes. La ligne supplementaire n'est pas renvoyee : elle sert uniquement a savoir si `nextCursor` doit etre produit.

Requete SQL envoyee a PostgreSQL pour une page apres un curseur :

```sql
SELECT orders.id, orders.restaurant_id, orders.user_id, orders.status,
       orders.total_amount_cents, orders.currency, orders.created_at,
       orders.updated_at
FROM orders
WHERE (orders.created_at, orders.id) < (:cursor_created_at, :cursor_id)
ORDER BY orders.created_at DESC, orders.id DESC
LIMIT :limit_plus_one;
```

Un index composite dans le meme ordre permet a PostgreSQL de se positionner directement apres le curseur :

```sql
CREATE INDEX ix_orders_created_at_id_desc
ON orders (created_at DESC, id DESC);
```

Alternatives ecartees:
- `OFFSET`, car la base doit parcourir les lignes ignorees sur une page profonde et parce que des insertions peuvent decaler les resultats.
- Lire toutes les commandes puis decouper la liste en Python, car la quantite de donnees lue augmenterait avec la taille de la table.
- Plafonner silencieusement une demande superieure a 100, car cela masquerait une erreur du client.

## Etape 4

### Regles d'idempotence des paiements

- Le client fabrique une cle unique pour chaque intention de paiement et l'envoie dans le header obligatoire `Idempotency-Key`.
- La cle est conservee avec le paiement dans PostgreSQL sans expiration pour toute la duree de l'exercice.
- La premiere requete cree le paiement et renvoie `201`. Les rejeux avec la meme cle et la meme requete renvoient le meme paiement et le meme statut `201`.
- Une cle differente represente une nouvelle intention et cree donc un nouveau paiement, meme pour une commande deja payee.
- Une requete sans cle est refusee en `422 application/problem+json`; une cle deja associee a une autre requete est refusee en `409`.

La table `payments` impose une contrainte d'unicite sur `idempotency_key`. Cette
contrainte garantit un seul enregistrement meme si deux requetes utilisant la
meme cle arrivent simultanement. Apres un conflit d'insertion, l'API recharge et
renvoie le paiement cree par la premiere transaction.

Une empreinte SHA-256 de `order_id`, `method` et `card_token` est stockee avec la
cle. Elle permet de distinguer un rejeu legitime d'une reutilisation accidentelle
de la cle pour une autre requete sans conserver de donnee de carte brute.

Alternatives ecartees:
- Une cle generee par le serveur, car elle ne protegerait pas le premier appel contre la perte de sa reponse et le rejeu par le client.
- Renvoyer une erreur lors d'un rejeu identique, car le client devrait alors deviner si le paiement a reellement ete effectue.
- Un cache en memoire, car son contenu serait perdu au redemarrage et ne serait pas partage entre plusieurs instances de l'API.
