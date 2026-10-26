# Snake Python Docker

Jeu Snake avec backend Flask (classement des scores) conteneurise avec Docker.
Lab 4 Docker - TEK-UP.

## Lancer avec Docker Hub
docker run -d -p 8083:5000 -v snake_scores:/data linarabah/snake-py:v1

## Construire l'image
docker build -t snake-py:v1 .
