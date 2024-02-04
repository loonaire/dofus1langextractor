# Dofus 1 lang extractor

Il s'agit d'un outil qui permet d'extraire une grande partie des fichiers swf de dofus 1 en json. Certains fichiers sont ignorés (les raisons sont indiquées), le code n'est pas parfait mais il fonctionne.  
L'outil fonctionne avec les langs de dofus, de la version 1.14 à dofus retro 1.41 et les versions supérieures, les arguments xtra peuvent être utilisés pour extraire les fichiers lang de dofus avant la 1.14.

Cet outil est composé de 2 scripts:
- langextractor qui permet de transformer les fichiers dans lang/swf/*.swf en json
- mapextractor qui permet de transformer les fichiers des map dans maps/*.swf en json

Pour afficher l'aide:
```sh
python langextractor.py --help
```
```sh
python mapextractor.py --help
```

## Les fichiers qui peuvent être extrait:

- Alignment
- Classes
- Crafts
- Dialog
- Dungeons (revoir les noms de certains éléments mais complètement gérés)
- Effects
- Emotes
- FightChallenges
- Hints
- Houses (note: la variable H.ids est convertie en tant que string)
- Interactiveobjects
- Items
- Itemsets
- Jobs
- Kb
- Maps
- Monsters
- Names
- Npc
- Quests
- Ranks
- Rides
- Scripts
- Servers
- Skills
- Speakingitems
- Spells (certains texte des sorts ajoutés avec temporis retro 2 posent des problèmes à cause de caractères hexa et sont modifiés)
- States
- Titles
- TTG

## Les fichiers ignorés:

Ces fichiers sont ceux qui ne sont pas utiles, posent trop de problème pour l'extraction ou dont l'extraction n'a pas d'utilité:

- Audio (Le fichier n'a pas vraiment de sens et n'est pas vraiment utile à décompiler)
- Guilds (le fichier ne semble pas utile à décompiler)
- Lang (pour des raisons évidentes: ce ne sont que des variables de texte des interfaces)
- Pvp (peu d'informations dans le fichier, variables simple et peut être transféré à la main)
- shortcuts (volantaire, peu d'interet à l'extraire)
- subtitles
- timeszones