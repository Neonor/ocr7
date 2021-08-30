# Openclassroom Projet 7
## Implémentez un modèle de scoring

Cette librairie integre l'api de calcul et le Dashboard de présentation

* l'API REST de calcul est basé sur la librairie [Fastapi](https://fastapi.tiangolo.com/)
* le Dashboard est basé sur la librairie [Bokeh](https://bokeh.org/)

Le modèle de scoring se base sur les données kaggle de [Home Credit Default Risk](https://www.kaggle.com/c/home-credit-default-risk/overview)

l'objectif est d'obtenir un score pour la capacité du client à rembourser sont emprunt.
#### les fichiers a disposition

* application_{train|test}.csv
    * Données de base pour l'analyse divisé en 2 fichiers (données de training avec l'objectif et de test pour l'évaluation kaggle)


* bureau.csv & bureau_balance.csv
    * Données des crédits précédant des clients venant d'autre institution financiaire avec des données au mois


* POS_CASH_balance.csv & credit_card_balance.csv
    * Solds mensuel des clients pendant les périodes de crédit


* previous_application.csv
    * Les demandes de crédit précédendes des clients


* installments_payments.csv
    * l'historique de rembourcement des crédits précédents
    

### Structure des données
En partant des données de base, on les complète à partir des autres fichier en partant de calcul simple:
* le nombre de crédit contracté
* le cummule des crédits contractés
* la moyenne et les cummules des solds en fin de mois
* les retards de payment


### Fonction de cout
La fonction de cout a un objectif simple : minimiser les mauvais payeurs quite à en perdre quelques bons.


### Le model d'analyse
Le modèle utilisé est [Lightgbm](https://lightgbm.readthedocs.io/en/latest/index.html) (recherche des hyperparametres via [Optuna](https://optuna.org/))


### Utilisation de l'API
* /compute/
    * POST ?ID= : lance le calcul du score pour ID client donné
    * GET : récupère le résultat du dernier calcul de score lancer (vide si pas de précédant calcul ou si calcul en cours)


* /explainer/
    * POST ?ID= : lance le calcul d'interprétation du score pour ID client donné
    * GET : récupère le résultat du dernier calcul d'interprétation lancer (vide si pas de précédant calcul ou si calcul en cours)

### Configuration serveur
fichier de configuration : config.json
```json
{
    "host":"XXX.XXX.XXX.XXX",
    "port_api":8080, 
    "port_bokeh":5000, 
    "dns":"exemple.org"
}
```
* host -> ip local server
* port_api -> port api
* port_bokeh -> port bokeh
* dns -> DNS (optionnel)

### Utilisation du serveur

Démarrer l'api
```sh
python api.py
```

Démarrer le dashboard
```bash
python dashboard.py
```

Sur un serveur linux utilisant systemctl pour les services, les 2 process peuvent être lancer en tant que service