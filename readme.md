# k8s-kind-cluster: Running a Flask API + Postgres on Kubernetes (Kind)
  
This project is a hands-on example of how to run a Flask API with a Postgres database using **Kubernetes** locally, with [Kind](https://kind.sigs.k8s.io/).  
We’ll see how to create the cluster, what each manifest is for, and how to use the API with `curl` (or Python, if you prefer).

---

## How to build the API image and load it into Kind

1. **Build the Docker image locally:**

```bash
docker build -t hello-api:latest api/
```

2. **Load the image into the Kind cluster:**

```bash
kind load docker-image hello-api:latest --name project-test
```

> **Tip:**  
> The cluster name (`project-test`) should be the same as the one you used when creating Kind.  
> If you don’t remember, run `kind get clusters`.

Done! Now Kind’s Kubernetes will use your local image instead of trying to pull it from Docker Hub.  
After that, just apply the manifests as usual:

```bash
kubectl apply -f k8s/manifests/
```

---

## How to spin up the cluster

First, let’s create the local Kubernetes cluster using Kind.  
There’s a script ready for that:

```bash
./k8s/start-cluster.sh
```

What does this script do?
- Deletes the old cluster (if it exists)
- Creates a new cluster with the right ports mapped (including 8000 and 30080)
- Shows if the cluster started up fine

> **Tip:** The file `k8s/kind-config.yaml` is already set up to expose the necessary ports.

---

## Deployments: What are they and what are they for?

### **API Deployment (`api-deployment.yaml`)**

This manifest spins up your Flask API container in the cluster.  
It makes sure there’s always at least 1 pod running the API.  
There’s also an `initContainer` that waits for the database to be ready before starting the API (avoids connection errors).

### **Database Deployment (`postgress-deployment.yaml`)**

This one spins up the Postgres container.  
It also makes sure the database is always available in the cluster.

---

## Services: Exposing the apps

### **API Service (`api-service.yaml`)**

This service is of type `NodePort`, meaning it exposes the API outside the cluster, mapping port 8000 from the pod to port 30080 on your computer (host).  
So you can access the API at `http://localhost:30080/` or, if you set up `hostPort`, directly at `http://localhost:8000/`.

### **Database Service (`postgress-service.yaml`)**

This one is `ClusterIP`, so it’s only accessible inside the cluster.  
The API uses this service to talk to the database via DNS (`postgres-service:5432`).

---

## How to use the API

Once everything’s running, you can interact with the API using `curl` or any HTTP client.

### **1. Health check**

```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy", "database": "connected"}
```

### **2. Hello World**

```bash
curl http://localhost:8000/
```
Response:
```json
{"message": "Hello World from Kubernetes!"}
```

### **3. Create a client**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@email.com"}'
```
Response:
```json
{"message": "Client successfully created", "id": 1}
```

### **4. List clients**

```bash
curl http://localhost:8000/clients
```
Response:
```json
{
  "clients": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao@email.com",
      "created_at": "2025-05-30T12:34:15.123456"
    }
    // ...other clients
  ]
}
```

### **5. Test duplicate email error**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "João Silva", "email": "joao@email.com"}'
```
Response:
```json
{"error": "Email already exists"}
```

### **6. Test invalid data**

```bash
curl -X POST http://localhost:8000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "No Email"}'
```
Response:
```json
{"error": "Invalid input: name and email are required"}
```

---

## Testing everything at once (Python)

If you want to run all the tests at once, there’s a Python script ready:  
Just run:

```bash
python3 test_api.py
```

This script does:
- Health check
- Hello World
- Creates several clients
- Lists all clients
- Tests duplicate email error
- Tests invalid data error

---

## 💡 Final tips

- If you change `kind-config.yaml`, **always** run `start-cluster.sh`!
- If you change the API code, **rebuild** the image, do the `kind load docker-image ...` and re-apply the deployment.
- If you get a database connection error, check if the database pod is running and if the `initContainer` is in the API deployment.

---

Any questions, just open an issue or DM me!  
Happy testing and happy APIs!
