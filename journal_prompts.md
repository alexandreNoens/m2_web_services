# Journal de prompts - Groupe : Alexandre Noens

## Etape 0 - Relecture du contrat

**Ce qu'on a demande a l'IA :**
> Lire le sujet dans `exo.md`, puis relire le contrat `openapi.yml` et le
> journal `journal_decisions.md` afin de verifier leur coherence et de proposer
> des corrections adaptees a une petite application scolaire.

**Ce qu'elle a bien fait :**

- Elle a verifie que les cinq besoins du sujet correspondaient bien a cinq routes REST versionnees.
- Elle a controle les codes HTTP, la pagination, les prix en centimes et les dates au format RFC 3339.
- Elle a repere que `cardToken` devait etre obligatoire pour un paiement par carte.
- Elle a precise que les prix et le montant total d'une commande sont calcules par le serveur.
- Elle a aligne les erreurs de validation sur le code `422` utilise par FastAPI.
- Elle a mis a jour le contrat et le journal de decisions ensemble pour eviter qu'ils se contredisent.

**Ce qu'on a du corriger, et pourquoi :**

- L'IA a d'abord propose de supprimer la cle d'idempotence pour simplifier l'exercice. C'etait une erreur, car l'etape 4 du TP impose une cle obligatoire sur les paiements.
- La relecture du cours et du TP en ligne a montre que les erreurs doivent toutes avoir la meme forme. Le contrat utilise donc `application/problem+json`, y compris pour les erreurs de validation.
- Le profil exposait encore l'email et le telephone. Ces champs ont ete retires, car l'etape 5 precise qu'ils doivent rester en base et ne jamais etre renvoyes.

## Etape 0 - Verification avec le cours complet

**Ce qu'on a demande a l'IA :**
> Relire le cours et le TP disponibles en ligne, verifier le contrat par rapport
> a toutes les consignes, puis corriger le fonctionnement de l'idempotence.

**Ce qu'elle a bien fait :**

- Elle a retrouve dans le TP les exigences exactes de l'etape 4.
- Elle a rendu le header `Idempotency-Key` obligatoire et a indique que la cle est generee par le client.
- Elle a defini que la cle est stockee avec le paiement en base pour toute la duree de l'exercice.
- Elle a documente qu'un rejeu avec la meme cle renvoie exactement la meme reponse `201` sans creer un second paiement.
- Elle a prevu un `422` si la cle est absente et un `409` si elle est reutilisee pour une requete differente.
- Elle a verifie la syntaxe YAML et l'absence d'erreurs de formatage dans le diff.

**Ce qu'on a du corriger, et pourquoi :**

- Le contrat disait a la fois qu'une cle differente cree un nouveau paiement et qu'une commande deja payee est dans un etat incompatible. Ces deux regles se contredisaient.
- La regle finale choisie pour suivre le TP est la suivante : meme cle et meme requete, meme reponse sans nouvel effet ; cle differente, nouveau paiement ; commande annulee, erreur `409`.
- Les etapes futures ne sont pas encore ajoutees au contrat : le rate limiting et sa reponse `429` seront ajoutes a l'etape 6, puis le champ facultatif `promoCode` a l'etape 7.
