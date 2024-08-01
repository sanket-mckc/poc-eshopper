#!/bin/bash

# Define variables
DB_NAME="furniture_shop"
COLLECTION_NAME="catalog"
CSV_FILE_PATH="./furniture_catalog.csv"  # Update this path to the actual CSV file location
CONTAINER_NAME="mongodb"
MONGO_IMAGE="mongo:latest"
MONGO_INITDB_ROOT_USERNAME="admin"
MONGO_INITDB_ROOT_PASSWORD="password"

# Check if Podman is installed
if ! command -v podman &> /dev/null
then
    echo "Podman is not installed. Installing Podman..."
    brew install podman
fi

# Initialize and start Podman machine if not running
if ! podman machine ls | grep -q "Running"; then
    echo "Initializing Podman machine..."
    podman machine init

    echo "Starting Podman machine..."
    podman machine start
fi

# Pull MongoDB image
podman pull $MONGO_IMAGE

# Run MongoDB container
podman run -d --name $CONTAINER_NAME -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=$MONGO_INITDB_ROOT_USERNAME -e MONGO_INITDB_ROOT_PASSWORD=$MONGO_INITDB_ROOT_PASSWORD $MONGO_IMAGE

# Wait for MongoDB to start
sleep 10

# Copy CSV file to container
podman cp $CSV_FILE_PATH $CONTAINER_NAME:/furniture_catalog.csv

# Import CSV into MongoDB
podman exec -it $CONTAINER_NAME mongoimport --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db $DB_NAME --collection $COLLECTION_NAME --type csv --headerline --file /furniture_catalog.csv

echo "MongoDB setup and data import completed."
