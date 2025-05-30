#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Testando API...")
    
    # 1. Health check
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")
        return
    
    # 2. Hello World
    print("\n2. Hello World:")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 3. Criar clientes
    print("\n3. Criando clientes:")
    clientes = [
        {"name": "João Silva", "email": "joao@email.com"},
        {"name": "Maria Santos", "email": "maria@email.com"},
        {"name": "Pedro Costa", "email": "pedro@email.com"}
    ]
    
    for cliente in clientes:
        try:
            response = requests.post(f"{BASE_URL}/clients", json=cliente)
            print(f"Criando {cliente['name']}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Erro ao criar {cliente['name']}: {e}")
    
    # 4. Listar clientes
    print("\n4. Listando clientes:")
    try:
        response = requests.get(f"{BASE_URL}/clients")
        print(f"Status: {response.status_code}")
        clientes_response = response.json()
        print(f"Total de clientes: {len(clientes_response.get('clients', []))}")
        for cliente in clientes_response.get('clients', []):
            print(f"  - {cliente['name']} ({cliente['email']}) - ID: {cliente['id']}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 5. Teste de erro (email duplicado)
    print("\n5. Testando email duplicado:")
    try:
        response = requests.post(f"{BASE_URL}/clients", 
                               json={"name": "João Duplicado", "email": "joao@email.com"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 6. Teste de dados inválidos
    print("\n6. Testando dados inválidos:")
    try:
        response = requests.post(f"{BASE_URL}/clients", json={"name": "Sem Email"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_api()
