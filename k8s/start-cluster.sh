#!/bin/bash
set -e

echo "=== Deletando cluster Kind existente (se houver) ==="
kind delete cluster --name project-test || true

echo "=== Criando cluster Kind ==="
kind create cluster --config k8s/kind-config.yaml --name project-test

echo "=== Verificando se o cluster está funcionando ==="
kubectl get nodes
kubectl cluster-info

