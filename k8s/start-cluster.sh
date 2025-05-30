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

echo "=== Instalando ArgoCD Image Updater ==="
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml

echo "=== Aguardando ArgoCD ficar pronto ==="
kubectl wait --for=condition=available --timeout=180s deployment/argocd-server -n argocd

echo "=== Recuperando a senha inicial do admin do ArgoCD ==="
ARGOCD_PWD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo
echo "****************************************************"
echo " ArgoCD admin password:"
echo "     $ARGOCD_PWD"
echo "****************************************************"
echo