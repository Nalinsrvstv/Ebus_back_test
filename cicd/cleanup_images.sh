#!/bin/bash

# Define the name of the Docker image you want to delete
image_name="navin531/ebus_backend"

# List all Docker images with the specified name
image_ids=$(docker images -q $image_name)

# Loop through the list of image IDs and remove them
for image_id in $image_ids; do
    docker rmi $image_id
done

echo "Deleted Docker images with name: $image_name"