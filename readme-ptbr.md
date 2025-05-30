# k8s-kind-cluster: Subindo uma API Flask + Postgres no Kubernetes (Kind)
  
Esse projeto é um exemplo prático de como rodar uma API Flask com banco Postgres usando **Kubernetes** localmente, com o [Kind](https://kind.sigs.k8s.io/).  
Vamos ver como criar o cluster, pra que serve cada manifest, e como usar a API usando `curl` (ou Python, se preferir).

---

## Como buildar a imagem da API e subir pro Kind

1. **Build da imagem Docker localmente:**

```bash
docker build -t hello-api:latest api/
```

2. **Carregar a imagem no cluster Kind:**

```bash
kind load docker-image hello-api:latest --name project-test
```

> **Dica:**  
> O nome do cluster (`project-test`) deve ser o mesmo que você usou ao criar o Kind.  
> Se não lembrar, rode `kind get clusters`.

Pronto! Agora o Kubernetes do Kind vai usar sua imagem local sem tentar puxar do Docker Hub.  
Depois disso, é só aplicar os manifests normalmente:

```bash
kubectl apply -f k8s/manifests/
```

---

## Como subir o cluster

Primeiro, vamos criar o cluster Kubernetes local usando o Kind.  
Deixei um script pronto pra isso:

```bash
./k8s/start-cluster.sh
```

O que esse script faz?
- Deleta o cluster antigo (se existir)
- Cria um novo cluster com as portas mapeadas certinho (inclusive 8000 e 30080)
- Mostra se o cluster subiu direitinho

> **Dica:** O arquivo `k8s/kind-config.yaml` já está configurado pra expor as portas nescessarias.

---

## Deployments: O que são e pra que servem?

### **Deployment da API (`api-deployment.yaml`)**

Esse manifest sobe o container da sua API Flask no cluster.  
Ele garante que sempre vai ter pelo menos 1 pod rodando a API.  
Além disso, tem um `initContainer` que espera o banco ficar pronto antes de subir a API (evita erro de conexão).

### **Deployment do Banco (`postgress-deployment.yaml`)**

Serve para subir o container do Postgres.  
Também garante que o banco vai estar sempre disponível no cluster.

---

## Services: Expondo as aplicações

### **Service da API (`api-service.yaml`)**

Esse service é do tipo `NodePort`, ou seja, ele expõe a API pra fora do cluster, mapeando a porta 8000 do pod pra porta 30080 do seu computador (host).  
Assim, você pode acessar a API em `http://localhost:30080/` ou, se configurou o `hostPort`, direto em `http://localhost:8000/`.

### **Service do Banco (`postgress-service.yaml`)**

Esse é do tipo `ClusterIP`, ou seja, só é acessível dentro do cluster.  
A API usa esse service pra conversar com o banco via DNS (`postgres-service:5432`).

---

## Como usar a API

Depois que tudo estiver rodando, você pode interagir com a API usando `curl` ou qualquer cliente HTTP.

### **1. Health check**

```bash
curl http://localhost:8000/health
```
Resposta esperada:
```json
{"status": "healthy", "database": "connected"}
```

### **2. Hello World**

```bash
curl http://localhost:8000/
```
Resposta:
```json
{"message": "Hello World from Kubernetes!"}
```

### **3. Criar um cliente**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@email.com"}'
```
Resposta:
```json
{"message": "Client successfully created", "id": 1}
```

### **4. Listar clientes**

```bash
curl http://localhost:8000/clients
```
Resposta:
```json
{
  "clients": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao@email.com",
      "created_at": "2025-05-30T12:34:15.123456"
    }
    // ...outros clientes
  ]
}
```

### **5. Testar erro de email duplicado**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@email.com"}'
```
Resposta:
```json
{"error": "Email already exists"}
```

### **6. Testar dados inválidos**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Sem Email"}'
```
Resposta:
```json
{"error": "Invalid input: name and email are required"}
```

---

## Testando tudo de uma vez (Python)

Se quiser rodar todos os testes de uma vez, tem um script Python pronto:  
Basta rodar:

```bash
python3 test_api.py
```

Esse script faz:
- Health check
- Hello World
- Cria vários clientes
- Lista todos os clientes
- Testa erro de email duplicado
- Testa erro de dados inválidos

---

## 💡 Dicas finais

- Se mudar o `kind-config.yaml`, **sempre** rode o `start-cluster.sh`!
- Se mudar o código da API, **rebuild** a imagem, faça o `kind load docker-image ...` e re-aplique o deployment.
- Se der erro de conexão com o banco, cheque se o pod do banco está rodando e se o `initContainer` está no deployment da API.

---

Qualquer dúvida, só abrir uma issue ou chamar no direct!  
Bons testes e boas APIs!