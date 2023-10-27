#!/bin/bash

set -exu

ROOT=$(cd "$(dirname "$0")/../" && pwd)

: "${PLATFORM:=linux/amd64}"

ARCH=$(echo "$PLATFORM" | cut -d/ -f2)

docker buildx build \
    --load \
    --platform "$PLATFORM" \
    -t "mysql-amazonlinux2023:$ARCH" \
    -f "$ROOT/Dockerfile.amazonlinux2023" "$ROOT"

mkdir -p amazonlinux2023.build
docker run \
    --rm \
    -v "$ROOT/amazonlinux2023.build:/output" \
    --platform "$PLATFORM" \
    "mysql-amazonlinux2023:$ARCH"
