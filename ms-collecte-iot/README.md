# ms-collecte-iot

Microservice de collecte IoT base sur une architecture ports/adapters.

- Consomme des donnees brutes depuis RabbitMQ
- Normalise les donnees dans un format commun
- Enregistre le resultat dans MongoDB
- Republie le message normalise dans RabbitMQ sur `collecte_queue`
