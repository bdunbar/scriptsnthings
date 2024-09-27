#!/bin/bash

# Ask for confirmation
read -p "Are you sure you want to delete all Docker containers and images? This action cannot be undone. (y/N): " -n 1 -r
echo    # Move to a new line

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Stop all containers
    docker stop $(docker ps -aq)

    # Remove all containers
    docker rm $(docker ps -aq)

    # Remove all images
    docker rmi $(docker images -q)

    # If you want to go full berserker and remove volumes and networks, uncomment the following lines:
    # docker volume rm $(docker volume ls -q)
    # docker network rm $(docker network ls -q)

    echo "The Vikings have done their job. Your Docker environment is clean!"
else
    echo "The Vikings hold back. Your Docker environment remains intact."
fi
