# Répertoire du Bot

Ce répertoire contient un bot Discord implémenté en Python. Le bot est conçu pour effectuer diverses tâches, telles que répondre à l'entrée de l'utilisateur et effectuer des actions automatisées.

## Installation

Pour installer le bot, suivez ces étapes :

1. Clonez le répertoire sur votre machine locale.
2. Installez les dépendances requises en exécutant `pip install -r requirements.txt`.

## Utilisation

1. [Accédez à la page des applications Discord.](https://discord.com/developers/applications)
2. Cliquez sur l'application de bot que vous avez créée.
3. Dans le menu de gauche, cliquez sur "Bot".
4. Sous "Token du bot", cliquez sur "Copier".
5. Collez le token dans un endroit sûr et ne le partagez avec personne.
6. Enfin, modifiez le programme main.py pour y inclure votre token:
```
bot = interactions.Client(token="Votre token")
```

## Contribution

Si vous souhaitez contribuer au bot, suivez ces étapes :

1. Fork le répertoire.
2. Créez une nouvelle branche pour vos modifications.
3. Effectuez vos modifications et commitez-les.
4. Poussez vos modifications vers votre fork.
5. Soumettez une pull request au répertoire principal.
