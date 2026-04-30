# Rapport Snyk - ms6-validateur-capteur

Ce document présente l'analyse Snyk du microservice `ms6-validateur-capteur`, les vulnérabilités identifiées avant correction, les corrections appliquées et l'impact sur la sécurité globale du service.

## 1. Rappel synthétique du scan initial

Le scan initial a été lancé sur le fichier `ms6-validateur-capteur/requirements.txt`.

```bash
snyk test --file=requirements.txt --package-manager=pip > snyk-report-avant.txt
```

Résultat avant correction :

- Dépendances testées : `12`
- Issues détectées : `2`
- Chemins vulnérables : `2`
- Dépendance vulnérable directe : `starlette@0.41.3`
- Dépendance ayant introduit Starlette : `fastapi@0.115.6`

## 2. Vulnérabilités CVE / Snyk identifiées

| Nom de la vulnérabilité | Sévérité | Dépendances concernées | Référence Snyk |
|---|---|---|---|
| Allocation of Resources Without Limits or Throttling | Medium | `fastapi@0.115.6` > `starlette@0.41.3` | `SNYK-PYTHON-STARLETTE-10874054` |
| Regular Expression Denial of Service (ReDoS) | High | `fastapi@0.115.6` > `starlette@0.41.3` | `SNYK-PYTHON-STARLETTE-13733964` |

### 2.1 Allocation of Resources Without Limits or Throttling

Cette vulnérabilité concerne `starlette@0.41.3`. Elle peut permettre à une requête malveillante ou anormalement volumineuse de consommer trop de ressources serveur, comme le CPU ou la mémoire.

Impact possible :

- dégradation des performances du microservice ;
- ralentissement des réponses HTTP ;
- risque d'indisponibilité partielle si le service est sollicité fortement.

La sévérité indiquée par Snyk est `Medium`.

### 2.2 Regular Expression Denial of Service (ReDoS)

Cette vulnérabilité concerne aussi `starlette@0.41.3`. Une entrée spécialement construite peut exploiter un traitement par expression régulière trop coûteux et provoquer un temps de calcul excessif.

Impact possible :

- blocage ou ralentissement important du traitement d'une requête ;
- consommation excessive du CPU ;
- risque de déni de service applicatif.

La sévérité indiquée par Snyk est `High`, donc cette correction était prioritaire avant tout déploiement en production.

## 3. Corrections appliquées

Le fichier `ms6-validateur-capteur/requirements.txt` a été corrigé avec les versions suivantes :

```text
fastapi==0.121.0
starlette==0.49.1
uvicorn==0.34.0
pydantic==2.10.4
pika==1.3.2
```

La correction principale est le remplacement de `starlette@0.41.3` par `starlette@0.49.1`.

## 4. Justification détaillée des corrections

### 4.1 Pourquoi passer de `starlette@0.41.3` à `starlette@0.49.1` ?

Le rapport Snyk indique explicitement :

```text
Pin starlette@0.41.3 to starlette@0.49.1 to fix
```

Le choix de `starlette==0.49.1` suit donc la recommandation directe de Snyk. Cette version corrige les deux chemins vulnérables détectés :

- la limitation insuffisante des ressources ;
- le risque de ReDoS.

Le pin explicite de `starlette==0.49.1` évite aussi qu'une résolution automatique de dépendances réinstalle une version vulnérable de Starlette.

### 4.2 Pourquoi mettre à jour `fastapi` vers `0.121.0` ?

Dans le scan initial, `starlette@0.41.3` était introduit par `fastapi@0.115.6`. Mettre à jour FastAPI permet d'aligner le framework principal avec une version compatible avec `starlette==0.49.1`.

Cette correction est importante car FastAPI dépend fortement de Starlette pour le routage et le traitement HTTP. Garder une ancienne version de FastAPI tout en forçant une version plus récente de Starlette aurait pu créer un risque d'incompatibilité.

Le remplacement par `fastapi==0.121.0` permet donc :

- de conserver une version récente du framework ;
- d'utiliser une version non vulnérable de Starlette ;
- de réduire le risque de conflit de dépendances ;
- de garder un comportement cohérent avec les tests du microservice.

### 4.3 Pourquoi conserver les autres dépendances ?

Les autres dépendances applicatives présentes dans `requirements.txt` ne sont pas signalées comme vulnérables dans le rapport Snyk :

- `uvicorn==0.34.0`
- `pydantic==2.10.4`
- `pika==1.3.2`

Elles ont donc été conservées afin de limiter le changement au strict nécessaire. Cette approche réduit le risque de régression fonctionnelle.

## 5. Vérification après correction

Après correction, un second scan Snyk a été exécuté. Le fichier `ms6-validateur-capteur/snyk-report-avant_2.txt` indique :

```text
Tested 13 dependencies for known issues, no vulnerable paths found.
```

Résultat après correction :

- Dépendances testées : `13`
- Chemins vulnérables : `0`
- Vulnérabilités connues détectées : `0`

La correction est donc validée par Snyk sur les dépendances Python du microservice.

## 6. Impact sur la sécurité globale

Avant correction, le microservice ne devait pas être considéré comme déployable en production, car une vulnérabilité de sévérité `High` était présente sur une dépendance centrale de l'application.

Après correction :

- les vulnérabilités Snyk détectées sont corrigées ;
- aucun chemin vulnérable connu n'est remonté par le scan après correction ;

Conclusion : du point de vue des dépendances analysées par Snyk, le microservice `ms6-validateur-capteur` est déployable en production après correction.

