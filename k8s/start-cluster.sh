#!/bin/bash
set -e

echo "=== Deletando cluster Kind existente (se houver) ==="
kind delete cluster --name project-test || true

echo "=== Criando cluster Kind ==="
kind create cluster --config k8s/kind-config.yaml --name project-test

echo "=== Verificando se o cluster está funcionando ==="
kubectl get nodes
kubectl cluster-info

echo "=== Instalando ArgoCD ==="
kubectl create namespace argocd || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "=== Aguardando ArgoCD ficar pronto ==="
kubectl wait --for=condition=available --timeout=180s deployment/argocd-server -n argocd

echo "=== Alterando senha do admin do ArgoCD ==="
# Gera o hash da senha 'admim123'
HASH=$(kubectl -n argocd exec deploy/argocd-server -- argocd-util hash-password admim123 | tail -n1)

kubectl -n argocd patch secret argocd-secret \
  -p "{\"stringData\": {\"admin.password\": \"$HASH\", \"admin.passwordMtime\": \"$(date +%FT%T%Z)\"}}"

echo "=== Reiniciando o pod do ArgoCD Server para aplicar a nova senha ==="
kubectl -n argocd delete pod -l app.kubernetes.io/name=argocd-server

echo "=== Pronto! ArgoCD instalado e senha do admin alterada para 'admim123' ==="