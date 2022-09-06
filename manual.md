# Manuel mTag (branche 'sauser')

mTag est une application qui permet l'inventaire à l'aide d'étiquettes munies d'un code QR. Elle permet d'inventorier des étagères (shelf), des jeux de gabarits (set) dont les pièces (part) sont placées dans des boîtes (box).

À l'heure actuelle, mTag fonctionne en mode offline, et ne permet pas de consulter le stock. Comme mTag est dans une phase de développement précoce, il est recommandé de n'interrompre la procédure d'inventaire sous aucun prétexte, sauf lorsque les objets en cours sont complets (toutes les boîtes d'une étagère doivent avoir été inventoriée ; de même, toutes les pièces d'un gabarit doivent avoir été inventoriées.

## Comment procéder

### Saisie des étagères
* Coller une étiquette sur l'étagère
* presser le bouton "+ shelf" et scanner le code QR
* optionnel : prendre un photo de l'étagère
* presser le bouton "+k/v"
* presser le bouton "key" pour faire apparaître le texte "location"
* dans la zone de texte du bas, indiquer où se trouve l'étagère
* presser le bouton "save + scan"
* presser le bouton "save" ; la référence de l'étagère est enregistré pour les boîtes qui suivent

### Saisie des jeux

* coller l'étiquette sur la documentation de celui-ci, ou sur une liste préparée au préalable
* presser le bouton "+ set" et scanner le code QR
* optionnel : prendre une photo de l'ensemble des pièces du jeu, arrangées sur une surface
* presser le bouton "+k/v"
* presser une fois le bouton "key" pour faire apparaître la valeur "set_id"
* dans la zone de texte du bas, indiquer le numéro de référence interne du jeu
* presser le bouton "+k/v"
* presser deux fois le bouton "key" pour faire apparaître la valeur "vehicle_type"
* dans la zone de texte du bas, indiquer le véhicule auquel correspond le jeu
* presser le bouton "save + scan" ; la référence du jeu est enregistrée pour les pièces qui suivent ; l'application demande automatiquement de scanner la première boîte correspondante

### Saisie des boîtes

* coller l'étiquette sur la boîte, scanner le code QR
* optionnel : prendre la boîte en photo
* presser le bouton "+k/v"
* presser une fois le bouton "key" pour faire apparaître la valeur "box_type"
* dans la zone de texte du bas, indiquer le type de caisse (cela facilite la recherche ultérieure)
* presser le bouton "+k/v"
* presser deux fois le bouton "key" pour faire apparaître la valeur "tare"
* dans la zone de texte du bas, indiquer le poids à vide de la caisse
* presser le bouton "save + scan" ; la référence du de la boîte est enregistrée pour les pièces qui suivent ; l'application demande automatiquement de scanner la première pièce du jeu

### Saisie des pièces
* coller l'étiquette sur la pièce, scanner le code QR
* prendre la pièce en photo
* presser le bouton "+k/v"
* presser une fois le bouton "key" pour faire apparaître la valeur "number_in_set"
* dans la zone de texte du bas, indiquer le numéro de la pièce
* presser le bouton "+k/v"
* presser deux fois le bouton "key" pour faire apparaître la valeur "weight"
* dans la zone de texte du bas, indiquer le poids de la pièce


Si la boîte est pleine:
* presser le bouton "+k/v"
* presser le bouton "cancel"
* presser le bouton "save"
* presser le bouton "+ box", puis effectuer la saisie de la nouvelle boîte

S'il reste de la place dans la boîte:
* presser le bouton "save + scan" ; l'application demande automatiquement de scanner une autre pièce

Si c'est la dernière pièce du jeu, voir ci-dessus


### Passer à un nouveau jeu
Une fois le poids de la dernière pièce saisie,

* presser le bouton "+k/v"
* presser le bouton "cancel"
* presser le bouton "save"
* presser le bouton "+ set", puis effectuer la saisie du nouveau jeu comme indiqué ci-dessus

### Passer à une nouvelle étagère
Une fois le poids de la dernière pièce saisie,

* presser le bouton "+k/v"
* presser le bouton "cancel"
* presser le bouton "save"
* presser le bouton "+ shelf", puis effectuer la saisie de la nouvelle étagère comme indiqué ci-dessus

Il est important de noter que les boîtes d'un jeu peuvent être réparties sur plusieurs étagères.

### Fin d'une période de saisie
Pour éviter de saturer la mémoire du téléphone, il est recommandé de presser le bouton "export DB" pérdiodiquement, de préférence à la fin d'un jeu ou d'une étagère ; la liste sur l'écran d'acceuil est vidée, les informations sont enregistrées dans un fichier zip (à télécharger sur l'ordinateur et me transmettre). La référence de l'étagère en cours, du jeu en cours, et de la boîte en cours restent en mémoire.


## Précautions pour l'étiquettage

**IMPORTANT** : la surface doit être plane ou presque (on ne peut généralement pas les coller sur des cylindres ; vérifier en cas de doute et si ça ne scanne pas, jeter l'étiquette et en coller une nouvelle ailleurs.

Les étiquettes sont à base de PET et relativement résistantes ; toutefois, en particulier dans le cadre d'un atelier et de pièces qui sont susceptibles d'êtres déplacées ou griffées, il est recommandé de:

* dégraisser la surface à l'essence ou acétone
* coller l'étiquette sur l'objet
* appliquer une couche de vernis incolore pour sécuriser l'étiquette
