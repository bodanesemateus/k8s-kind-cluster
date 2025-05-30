# k8s-kind-cluster: Running a Flask API + Postgres on Kubernetes (Kind)
  
This project is a hands-on example of how to run a Flask API with a Postgres database using **Kubernetes** locally, with [Kind](https://kind.sigs.k8s.io/).  
We’ll see how to create the cluster, what each manifest is for, and how to use the API with `curl` (or Python, if you prefer).

---

## How to build the API image and load it into Kind

1. **Build the Docker image locally:**

```bash
docker build -t hello-api:latest api/
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

- Installs ArgoCD and sets the admin password to `admim123`


## GitOps with ArgoCD

This project comes with [ArgoCD](https://argo-cd.readthedocs.io/) set up for GitOps.  
ArgoCD keeps an eye on your GitHub repo and automatically applies any changes you make to the Kubernetes manifests.

How it works here:
- The folder `argocd/` has the ArgoCD Application manifest (`app.yaml`).
- When you run `start-cluster.sh`, ArgoCD is installed and configured.
- Any change you push to the manifests in this repo will be picked up and applied by ArgoCD automatically.

To access the ArgoCD UI locally:

```bash
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

Then open [https://localhost:8081](https://localhost:8081) in your browser.
Login: `admin`

Password: (the script will print the initial password in the terminal, highlighted between asterisks)

> The initial ArgoCD admin password is generated automatically and will be shown in your terminal after running `start-cluster.sh`.

---

## Automatic Image Updates with ArgoCD Image Updater

### What is ArgoCD Image Updater?

[ArgoCD Image Updater](https://argocd-image-updater.readthedocs.io/) is a tool that automates the process of updating container image tags in your Kubernetes manifests.  
It watches your container registries (like Docker Hub) for new image versions and, when it finds a new tag (for example, a new release of your API), it automatically updates your manifests in the Git repository and triggers a new deployment via ArgoCD.

**In short:**  
You push a new image to Docker Hub → Image Updater detects it → updates the manifest in Git → ArgoCD deploys the new version automatically.  
This is true GitOps: your cluster state always matches what’s in Git, and your images are always up-to-date.

### How is it implemented here?

- The folder `argocd/` contains:
  - `app.yaml`: The ArgoCD Application manifest, with annotations for the Image Updater.
  - `image-updater.secret.yaml`: Secret with configuration for the Image Updater (template, see below).
  - `repo-credentials.yaml`: Secret with credentials for ArgoCD to access your GitHub repo (template, see below).

- The `app.yaml` manifest is annotated to tell Image Updater which image to watch and how to update it.

- The Image Updater is installed and runs in the `argocd` namespace, watching for new image tags and updating the manifests in your GitHub repo automatically.

### How to configure secrets securely

**Never commit your real GitHub token in the repository!**  
Instead, version only the template files and inject the real values at deploy time.

#### 1. `image-updater.secret.yaml` (template)

```yaml
apiVersion: v1  
kind: Secret  
metadata:
  name: argocd-image-updater-config
  namespace: argocd  
stringData:  
  log.level: debug  
  registries.conf: | 
    registries:
    - name: Docker Hub
      prefix: docker.io
      api_url: https://registry-1.docker.io
  git.config: |  
    commit_message_template: "chore: update image to {{.NewTag}}"
    author_name: "ArgoCD Image Updater"
    author_email: "argocd-image-updater@example.com"
  git-credentials: |
    https://bodanesemateus:$YOUR_GITHUB_TOKEN@github.com
```

#### 2. `repo-credentials.yaml` (template)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: repo-github-k8s-credentials
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository 
stringData:
  type: git 
  url: https://github.com/bodanesemateus/k8s-kind-cluster.git
  username: $YOUR_GITHUB_USERNAME
  password: $YOUR_GITHUB_TOKEN
  log.level: debug
```

**Replace** `$YOUR_GITHUB_TOKEN` and `$YOUR_GITHUB_USERNAME`.

---

### How to check if Image Updater is working

- Check the logs of the Image Updater pod:

```bash
kubectl logs -n argocd deployment/argocd-image-updater
```

- When you push a new image to Docker Hub, the Image Updater should detect it, update the manifest in your repo, and ArgoCD will deploy the new version.

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
