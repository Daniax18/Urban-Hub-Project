# Rapport SonarCloud - ms6-validateur-capteur

Ce document reprend l'analyse SonarCloud réalisée pour le microservice `ms6-validateur-capteur`.
Toutes les alertes identifiées sont de niveau **Medium** ; il n'y a pas de critique (`Critical`) ni de haut niveau (`High`).

## 1. Résumé général

- Quality Gate : `Passed` avec avertissement
- Open issues : `2` en **Reliability**
- Security issues : `0`
- Security Hotspots : `1`
- Sévérité : uniquement **Medium**

## 2. Détail des issues

### 2.1 Security Hotspot
- Nom de la balise : `Security Hotspot`
- Signification : élément de code ou configuration nécessitant une revue de sécurité manuelle
- Cause : le `Dockerfile` du microservice utilise l'utilisateur par défaut `root` pour l'image Python
- Action : revoir l'exécution du conteneur, privilégier un utilisateur non privilégié 
- Impact : en cas de compromission, un attaquant pourrait obtenir des privilèges étendus dans le conteneur et accéder/modifier des données sensibles

### 2.2 Reliability
- Nom de la balise : `Reliability`
- Signification : problème de robustesse du code pouvant entraîner un comportement incorrect ou des erreurs non détectées
- Cause : comparaison de valeurs flottantes avec l'opérateur `==` dans des tests
- Action : remplacer la comparaison directe par un entier pour le moment. Dans la continuité du projet, utilisation du `pytest.approx`
- Impact : les comparaisons de flottants peuvent échouer à cause des imprécisions numériques, ce qui conduit à des résultats de test instables ou erronés

## 3. Issues vues

1. Reliability (Medium)
2. Security Hotspot (Medium)

## 4. Conclusion

L'analyse montre deux issues principales, toutes deux de niveau **Medium**. Aucune alerte `Critical` ou `High` n'a été détectée. Les correctifs doivent se concentrer sur la robustesse des comparaisons numériques et sur l'exécution sécurisée du conteneur Docker.
