# Kubernetes Reference Manifests

These manifests are **not deployed** — this project runs on a single server
using Docker Compose, which is the correct tool for the scale.

They exist to demonstrate understanding of Kubernetes concepts and to
document how this project would be deployed in a production environment
with multiple nodes, auto-scaling, and high availability.

## When would you use K8s instead of Docker Compose?

- **Multiple servers** — K8s orchestrates containers across a cluster of nodes.
- **Auto-scaling** — K8s can spin up more backend pods under high load.
- **Rolling updates** — Deploy new versions with zero downtime.
- **Health checks** — Automatically restart failed containers and route traffic away.
- **Service discovery** — Containers find each other by name without hardcoded IPs.

## Why Docker Compose is correct for this project

- **Single server** (MacBook Air with 3.7GB RAM)
- **Three containers** (HA, backend, frontend + nginx)
- **Single user** (personal home automation)
- **No need for auto-scaling** (one user, one TV, a few lights)
- K8s control plane alone would consume 500MB-1GB of RAM on this hardware.
