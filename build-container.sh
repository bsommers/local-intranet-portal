#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

TOOL="${1:-docker}" # default to docker, or pass 'podman' / 'buildah'

if [ "$TOOL" = "buildah" ]; then
    echo "Building container image with Buildah..."
    buildah bud -t local-intranet-portal:latest -f Dockerfile .
    echo "Buildah build complete: local-intranet-portal:latest"
elif [ "$TOOL" = "podman" ]; then
    echo "Building container image with Podman..."
    podman build -t local-intranet-portal:latest .
    echo "Podman build complete: local-intranet-portal:latest"
else
    echo "Building container image with Docker..."
    docker build -t local-intranet-portal:latest .
    echo "Docker build complete: local-intranet-portal:latest"
fi
