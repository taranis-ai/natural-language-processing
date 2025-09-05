#!/bin/bash

set -eou pipefail

cd $(git rev-parse --show-toplevel)

GITHUB_REPOSITORY=${GITHUB_REPOSITORY:-"ghcr.io/taranis-ai"}
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9_.-]/_/g')
MODEL=${MODEL:-"gliner"}

echo "Building containers for branch ${CURRENT_BRANCH} with the repository ${GITHUB_REPOSITORY} with model ${MODEL}"
echo "$TAG_BOT"
echo "$BOT_API_KEY"

docker buildx build --file Containerfile \
  --build-arg GITHUB_REPOSITORY="${GITHUB_REPOSITORY}" \
  --build-arg MODEL="${MODEL}" \
  --tag "${GITHUB_REPOSITORY}/taranis-nlp-bot:latest" \
  --tag "${GITHUB_REPOSITORY}/taranis-nlp-bot:${CURRENT_BRANCH}" \
  --tag "${GITHUB_REPOSITORY}/taranis-nlp-bot:${MODEL}" \
  --load .
