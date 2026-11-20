# Preuves - Etape 4

Le client genere une cle pour chaque intention de paiement et l'envoie dans le
header `Idempotency-Key`. Le serveur conserve cette cle avec le paiement. Un
rejeu strictement identique renvoie donc le paiement deja enregistre avec le
meme statut `201`, sans produire un nouvel effet en base.

## Verification avec Make

L'API et PostgreSQL doivent etre demarres. Depuis ce dossier :

```bash
make check
make replay-payment
make different-key
make missing-key
```

Chaque execution genere de nouvelles cles horodatees. Les preuves peuvent ainsi
etre rejouees sans vider la table `payments`.

`make check` verifie automatiquement que :

- les trois appels avec la meme cle renvoient `201 application/json` ;
- les trois corps de reponse sont strictement identiques ;
- une seule ligne utilise cette cle dans la table `payments` ;
- une autre cle cree un paiement avec un autre identifiant ;
- les deux cles correspondent bien a deux lignes en base ;
- l'absence de cle renvoie `422 application/problem+json` avec un message clair.

## Capture demandee

Executer `make replay-payment` puis capturer le terminal. La premiere partie
affiche les trois reponses sous les noms `reponse1`, `reponse2` et `reponse3`.
Leurs champs, notamment `id` et `paidAt`, sont identiques. La seconde partie
interroge directement PostgreSQL et ne montre qu'une ligne pour la cle utilisee.

![Trois reponses identiques et une seule ligne de paiement](paiement_idempotent_rejoue.png)

La sortie a la forme suivante :

```text
========== TROIS REPONSES ==========
{
  "reponse1": { "id": "...", "status": "succeeded", "paidAt": "..." },
  "reponse2": { "id": "...", "status": "succeeded", "paidAt": "..." },
  "reponse3": { "id": "...", "status": "succeeded", "paidAt": "..." }
}
========== TABLE PAYMENTS ==========
                  id                  | ... |          idempotency_key
--------------------------------------+-----+------------------------------------
 ...                                  | ... | etape-4-replay-...
(1 row)
```

`make different-key` affiche deux paiements possedant des identifiants
differents, puis les deux lignes correspondantes en base. `make missing-key`
affiche le refus de la requete et le detail `header.Idempotency-Key: Field
required`.

## Protection en base

La colonne `payments.idempotency_key` possede une contrainte d'unicite. Elle
garantit qu'une seule requete peut enregistrer une cle, y compris si deux appels
arrivent simultanement. En cas de conflit concurrent, l'API recharge le paiement
deja valide et renvoie cette meme reponse.

Une empreinte SHA-256 de l'identifiant de commande et du corps metier est aussi
conservee. Si un client reutilise une cle pour une requete differente, l'API
renvoie un conflit `409` au lieu de retourner un paiement qui ne correspond pas
a sa demande.
