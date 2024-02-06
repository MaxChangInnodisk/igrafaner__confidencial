#!/bin/bash

# Move to docker folder
DOCKER_FOLDER=$(dirname "${0}")
ROOT=$(dirname ${DOCKER_FOLDER})
cd ${ROOT}

config_file="${DOCKER_FOLDER}/config.ini"
if [ ! -f "$config_file" ]; then
  echo "Error: Config file '$config_file' does not exist."
  exit 1
fi

# Get data
source <(grep = ${config_file})

# Check value is empty or not
if [ -z "$PROJECT" ] || [ -z "$VERSION" ] || [ -z "$DOCKERFILE" ]; then
  echo "Error: Configuration values are missing in '$config_file'. Please check the file format."
  exit 1
fi

# Logout
echo "Using Configuration from '$config_file':"
echo "PROJECT: $PROJECT"
echo "VERSION: $VERSION"
echo "DOCKERFILE: $DOCKERFILE"

# Build docker image
docker build \
-t "${PROJECT}:${VERSION}" \
-f "${DOCKER_FOLDER}/${DOCKERFILE}" .

# Done
echo ""
echo "FINISHED !"
