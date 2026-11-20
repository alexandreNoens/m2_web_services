# Études de cas — Groupe : Alexandre Noens

## Cas 1
Les routes de l'intranet
★★★  ⏱ 12 min
Une appli de gestion de notes pour une école

Un développeur junior a livré ces cinq routes. Elles fonctionnent toutes.

```
GET   /getStudents
POST  /student/delete?id=4
GET   /Notes_list
POST  /updateNote
GET   /getStudentNotes?student=4&delete=true
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

Pas de verbe pour les ressources, il faut un nom au pluriel, l'action est le verbe HTTP.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Problème de communication entre le back et le front. Mauvais endpoint, perte de données.

- Quel principe du cours s'applique ?

L'architecture REST, des noms pour les ressources, des verbes HTTP pour les actions.

- Réécrivez les cinq routes proprement, avec leur méthode HTTP.

```
GET      /students
DELETE   /students/4
GET      /notes
POST     /notes
DELETE   /students/4
```

- La dernière ligne cache un danger particulier. Lequel ?

C'est un GET alors que c'est un DELETE


## Cas 2
La place F7
★★★  ⏱ 12 min
Une billetterie de cinéma

Deux personnes réservent la même place au même moment. Voici ce que reçoit la seconde. Son appli affiche « Réservation confirmée ».

```
POST /v1/bookings
{ "movieId": 12, "seat": "F7" }

HTTP/1.1 200 OK
Content-Type: application/json

{ "ok": false, "error": "E42" }
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

Le code HTTP est 200 OK et dans le message c'est écrit erreur. Si c'est une erreur il faut que le code soit 400.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Mauvaise gestion des erreurs côtés front, ça peut tromper l'utilisateur.

- Quel principe du cours s'applique ?

Les codes de statut HTTP, Un code à 3 chiffres. Le premier dit qui est responsable.

- Réécrivez la réponse complète : le code de statut, l'en-tête, le corps.

```
POST /v1/bookings
{ "movieId": 12, "seat": "F7" }

HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "title": "Reservation impossible",
  "detail": "Place déjà réservée",
  "status": 409
}
```

- Que voulait dire E42 ? Qui est censé le savoir ?

Une erreur, le backend avec normalement un message d'erreur. Mais sans l'envoi de ce message dans le backend, impossible pour le front de deviner.

## Cas 3
La page d'accueil met 9 secondes
★★★  ⏱ 12 min
Une boutique en ligne

La boutique a démarré avec 40 produits. Elle en a 80 000 aujourd'hui. La page d'accueil affiche 12 produits. Le code n'a pas changé depuis le lancement.

```
app.get('/v1/products', async (req, res) => {
  const products = await db.query('SELECT * FROM products');
  res.json(products);
});
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

La BDD renvoie tous les produits, il faudrait paginer.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Plus il y a de produits, plus la requête va être longue ; si le site devient lent, les utilisateurs ne vont pas rester et donc ne pas acheter.

- Quel principe du cours s'applique ?

La pagination, on renvoie une liste par morceaux, jamais en entier.

- À quoi doit ressembler la requête du front, et la réponse de l'API ? Écrivez les deux.

```
app.get('/v1/products?limit=20', async (req, res) => {
  const products = await db.query('SELECT * FROM products LIMIT 20');
  res.json(products);
});

{
  "data": [ 20 commandes ],
  "next_cursor": "def"   // la suite
}
```

- Le front demande 500 000 produits d'un coup. Que fait votre API ?

L'API ne renvoie que 20 produits, si l'utilisateur veut voir le reste, il doit cliquer sur la page 2.

## Cas 4
Trois dons de 20 €
★★★  ⏱ 12 min
Une cagnotte en ligne

Léa donne 20 € pour le pot de départ d'un collègue, depuis le train. Le réseau coupe au moment où elle valide. L'appli réessaie automatiquement. Son relevé affiche trois débits de 20 €.

```
app.post('/v1/donations', async (req, res) => {
  const don = await db.donations.insert({
    cagnotteId: req.body.cagnotteId,
    montant: req.body.montant,
  });
  await banque.debiter(req.user.carte, req.body.montant);
  res.status(201).json(don);
});
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

L'API ne vérifie pas l'id d'une transaction, elle peut donc se répéter plusieurs fois.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

L'utilisateur peut être débité plusieurs fois, il faut donc les rembourser. Problème de SAV.

- Quel principe du cours s'applique ?

L'idempotence, faire l'action 1 fois ou 10 fois donne exactement le même résultat.

- Décrivez la solution étape par étape : que fait l'appli, que fait le serveur au premier envoi, que fait-il au deuxième ?

Le front envoie la requête de paiement avec une clé,
l'API ne connaît pas cette clé,
le client est débité

le front envoie une deuxième requête de paiement avec la même clé,
l'API connaît déjà cette clé, elle ne fait rien.
le client n'est pas débité à nouveau

- Regardez l'ordre des deux opérations dans le code. Que se passe-t-il si le débit échoue ?

La donation est d'abord enregistrée avant le débit, il faut faire l'inverse.

## Cas 5 
La fiche du conducteur
★★★  ⏱ 12 min
Une appli de covoiturage

Avant un trajet, le passager voit la fiche du conducteur : son prénom et sa note. Voici ce que l'API renvoie pour afficher ces deux informations.

```
GET /v1/drivers/12

HTTP/1.1 200 OK

{
  "id": 12,
  "firstName": "Samir",
  "rating": 4.8,
  "phone": "06 44 21 08 77",
  "homeAddress": "8 allée des Tilleuls, Nantes",
  "iban": "FR76 3000 4000 0312 3456 7890 143",
  "passwordHash": "$2b$10$Kq1...",
  "licenseNumber": "14AB12345"
}
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

L'API renvoie trop d'informations, on n'a pas besoin de tout cela.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Fuite de données, RGPD.

- Quel principe du cours s'applique ?

L'exposition excessive de données
L'API renvoie des champs que le client n'a pas à voir.

- Classez les 8 champs en trois colonnes : visible par tous, réservé au conducteur lui-même, ne sort jamais de l'API.

Visible par tous : 
  "id": 12,
  "firstName": "Samir",
  "rating": 4.8,

Réservé au conducteur lui-même :
  "phone": "06 44 21 08 77",
  "homeAddress": "8 allée des Tilleuls, Nantes",
  "iban": "FR76 3000 4000 0312 3456 7890 143",

Ne sort jamais de l'API :
  "passwordHash": "$2b$10$Kq1...",
  "licenseNumber": "14AB12345"

- « Ce n'est pas grave, le front ne les affiche pas. » Que répondez-vous ?

Ce n'est pas parce que ce n'est pas visible dans le HTML que c'est invisible, F12, le body des requêtes, etc.

## Cas 6
La facture de mars
★★★  ⏱ 15 min
Une API météo gratuite

Cette API revend les prévisions d'un fournisseur qui facture chaque appel. Elle est ouverte à tous, sans inscription. En mars, un site partenaire met en ligne une page qui interroge l'API toutes les secondes pour chacun de ses visiteurs. La facture du fournisseur est multipliée par 40.

```
app.get('/v1/forecast', async (req, res) => {
  const meteo = await fournisseur.previsions(req.query.ville);  // 0,002 € par appel
  res.json(meteo);
});
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

C'est une API publique, sans limite d'accès. N'importe qui peut faire autant de demandes qu'il souhaite et donc nous faire payer à chaque fois.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Surcharge du service, facture qui explose, problème de latence voire d'indisponibilité.

- Quel principe du cours s'applique ?

Le rate limiting, un quota de requêtes par client. Au-delà, l'API refuse.

- Que mettez-vous en place ? Précisez : qui est compté, quelle limite, et ce que l'API répond quand elle est dépassée.

Un quota, X requêtes par X minutes pour un utilisateur 
Quand ce quota est dépassé, renvoyez le code HTTP 429 Too Many Requests     

- Vous limitez par adresse IP. Une école de 800 étudiants sort sur Internet avec une seule adresse. Que se passe-t-il ?

Chaque étudiant a la même adresse IP, le site croit que c'est une seule personne qui appelle 800 fois, alors que c'est un utilisateur différent à chaque fois.

- La météo de Lyon change-t-elle toutes les secondes ? Qu'est-ce que ça vous suggère en plus ?

Pas besoin d'avoir la météo chaque seconde, une fois par heure suffit.


## Cas 7

La mise à jour du 3 mars
★★★  ⏱ 15 min
Une banque mobile

L'appli de la banque est installée sur 200 000 téléphones. Voici les notes de la mise à jour de l'API. Le lendemain, le support reçoit 4 000 appels.

```
## Version 1 — mise à jour du 3 mars

- Ajout du champ `currency` dans la réponse de GET /v1/accounts/{id}
- Le champ `balance` s'appelle maintenant `availableBalance`
- Suppression du champ `iban` (peu utilisé)
- Nouveau paramètre obligatoire `reason` sur POST /v1/transfers
- Ajout de la route GET /v1/accounts/{id}/cards
```

🤔 Votre analyse

- Pour chacune des 5 lignes : cassante ou non cassante ? Justifiez en pensant à une appli installée il y a six mois.

    - Ajout du champ `currency` dans la réponse de GET /v1/accounts/{id}

    Non cassant, il suffira d'ajouter ce champ dans le front.

    - Le champ `balance` s'appelle maintenant `availableBalance`

    Cassant, la ressource n'est plus affichée côté front, car le nom a changé.

    - Suppression du champ `iban` (peu utilisé)

    Cassant, ce n'est pas parce que c'est peu utilisé qu'il faut le supprimer.

    - Nouveau paramètre obligatoire `reason` sur POST /v1/transfers

    Cassant, si le front n'est pas à jour, impossible de faire des transferts.

    - Ajout de la route GET /v1/accounts/{id}/cards

    Non cassant, il faudra ajouter une nouvelle page.

- Quel dégât concret pour la banque ?

SAV saturée, perte de confiance, perte de clients.

- Quel principe du cours s'applique ?

Le versioning, une API publiée est une promesse. On ne la casse pas.

- Réécrivez le plan de mise à jour : qu'est-ce qui peut partir dans la version 1, qu'est-ce qui demande une version 2, et que devient la version 1 ?

Version 1 :
- Ajout du champ `currency` dans la réponse de GET /v1/accounts/{id}
- Ajout de la route GET /v1/accounts/{id}/cards

Version 2 :
- Le champ `balance` s'appelle maintenant `availableBalance`
- Nouveau paramètre obligatoire `reason` sur POST /v1/transfers

La version 1 reste un backup pour les versions de l'app qui ne sont pas mises à jour par les utilisateurs.

- Comment obtenir le même résultat métier pour la ligne 2 sans rien casser ?

Modifier le contrat API, laisser l'ancien nom et ajouter le nouveau sous v2

## Cas 8 
La conversation
★★★  ⏱ 12 min
Une startup, deux développeurs

Extrait de la messagerie interne de l'équipe.

```
Sarah (front)  10:02   Tu renvoies quoi pour une commande ? J'ai besoin du prix et de la date
Tom (back)     10:15   {price, date} en gros
Sarah (front)  10:16   ok je pars là-dessus
        ... trois semaines plus tard ...
Sarah (front)  16:40   pourquoi j'ai "amount_cents": 2490 et "created": 1795000000 ???
Tom (back)     16:52   bah c'est le prix et la date
Sarah (front)  16:53   moi j'affiche "2490 €" et "Invalid Date" sur tous les écrans
Tom (back)     17:05   ah. et le champ s'appelle amount_cents depuis lundi, j'avais prévenu Karim
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

Le front et le back communiquent mal, les données ne sont pas cohérentes.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Problème d'affichage, de valeurs, de prix.

- Quel principe du cours s'applique ?

Le contrat d'API, un fichier qui décrit toute l'API. Tout le monde code à partir de lui.

- Qu'aurait-il fallu produire le premier jour, avant d'écrire une ligne de code ? Décrivez ce document et ce qu'il contient pour cette route.

Rédiger un contrat API, pour chaque route il décrit :
- le nom de la route
- la méthode (GET, POST ect..)
- Ce que ça renvoie, le body
- Pour chaque cas de types d'erreurs, la réponse en détail.

- Relevez tous les malentendus de la conversation. Il y en a au moins quatre.

L'unité pour le prix n'a pas été définie
Le format de la date n'a pas été défini
Le nom du champ date a été renommé
Sarah aurait dû demander un contrat API

## Cas 9 
Le test qui dit toujours oui
★★★  ⏱ 12 min
Un site de vente

Ce test tourne à chaque mise en production. Il est vert.

```
test('le panier applique la remise de 10 %', async () => {
  const res = await api.post('/v1/carts/7/checkout', { promoCode: 'BIENVENUE10' });
  expect(res.status).toBe(200);
});

// En production : le total d'un panier de 50 € est de 40,50 € au lieu de 45 €.
// La remise est appliquée deux fois. Le test est vert depuis deux mois.
```

🤔 Votre analyse

- Où est le problème ? Décrivez-le en une phrase, comme à un collègue.

Le test ne teste que le code HTTP 200, ce n'est pas suffisant.

- Quel dégât concret : prix, sécurité ou scalabilité ? Donnez un exemple chiffré ou une situation.

Test inutile, c'est comme s'il n'y avait pas de test, problème impossible à relever.
Cela va prendre beaucoup de temps à corriger. Perte de temps et d'argent.

- Quel principe du cours s'applique ?

Les tests d'API, des programmes qui appellent l'API et vérifient la réponse tout seuls.

- Réécrivez ce test pour qu'il attrape le bug.

```
test('le panier applique la remise de 10 %', async () => {
  const res = await api.post('/v1/carts/7/checkout', { promoCode: 'BIENVENUE10' });
  expect(res.status).toBe(200);
  expect(res.data.total).toBe(45);
});
```

- Citez deux autres cas qu'il faudrait tester sur cette route.

Le total, si c'est le bon code promotion qui est appliquée et s'il est valide ?

## Cas 10
Sept lignes, combien de problèmes ?
★★★  ⏱ 20 min
Cas de synthèse

Cette route renvoie un client et ses commandes. Elle est en production. Trouvez tout ce qui ne va pas : il y a au moins six problèmes, et ils ne viennent pas tous de la même règle.

```
app.get('/getUserOrders', async (req, res) => {
  const user = await db.users.findById(req.query.id);
  const orders = await db.orders.find({ userId: user.id });
  res.status(200).json({ user: user, orders: orders });
});
```

🤔 Votre analyse

- Listez tous les problèmes que vous trouvez. Pour chacun : le principe du cours concerné.

    - Le nom de la route n'est pas bon. L'architecture REST, des noms pour les ressources, des verbes HTTP pour les actions.

    - Il manque l'id dans la route pour récupérer un utilisateur

    - La route renvoie l'utilisateur et sa commande, alors que la route s'appelle "get user orders", 
    L'exposition excessive de données, l'API renvoie des champs que le client n'a pas à voir.

    -  La route renvoie 200, les différents cas d'erreur ne sont pas testés
    Les codes de statut HTTP, un code à 3 chiffres. Le premier dit qui est responsable.

- Que se passe-t-il si l'identifiant demandé n'existe pas ? Suivez le code ligne par ligne.

La requête échoue, le code plante, erreur 500.

- Classez vos problèmes du plus grave au moins grave, et défendez votre classement.

Absence de gestion des erreurs HTTP :

Ce route va résulter en des erreurs 5XX, il ne faut pas que l'appli renvoie des erreurs 5XX.
Les erreurs doivent être gérées pour qu'il s'agisse d'erreurs 4XX.

La réponse renvoie l'utilisateur et sa commande :

Problème de fuite de données. RGPD.

Manque l'ID user :

La route ne fonctionne pas.

Mauvais nom de route :

Mauvais respect de la bonne pratique REST.

- Réécrivez la route entière, dans le langage de votre choix ou en pseudo-code.

```python
@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    user = await db.users.find_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Utilisateur introuvable"
        )

    orders = await db.orders.find({"userId": user_id})

    return {
        "orders": orders
    }
```
