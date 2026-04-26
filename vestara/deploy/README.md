# Vestara Deployment Guide

Deploy Vestara to any cloud platform that supports Docker containers.

## Prerequisites

- Docker 24.0+
- docker-compose v2.20+ (`docker compose` command)
- Git

## Local Testing with Docker Compose

```bash
# From the vestara/ directory (where docker-compose.yml lives)
cd vestara/

# Build and start
docker compose up --build

# Open in browser
open http://localhost:8501

# Stop
docker compose down
```

For live reload during development, uncomment the `volumes:` block in `docker-compose.yml`.

---

## Streamlit Community Cloud

Streamlit Community Cloud deploys directly from a GitHub repository.

### 1. Configure `.streamlit/config.toml`

Ensure `vestara/.streamlit/config.toml` exists (already included). Key settings:

```toml
[server]
headless = true
runOnSave = true

[browser]
gatherUsageStats = false
```

### 2. Create `vestara/requirements.txt`

Already included with pinned dependencies. Update versions as needed.

### 3. Commit and Push

```bash
git add deploy/ .streamlit/ requirements.txt
git commit -m "infra: add deployment configuration"
git push origin main
```

### 4. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select this repository:
   - **Repository**: `your-username/vestara`
   - **Branch**: `main`
   - **Main file path**: `vestara/src/ui/app.py`
5. Click **Deploy!**

The app will be available at `https://your-app-name.streamlit.app`.

### 5. Secrets Management (Optional)

For production, set secrets in the Streamlit Community Cloud dashboard under **Settings → Secrets**. Reference them in code via `st.secrets`:

```python
api_key = st.secrets["OPENAI_API_KEY"]
```

---

## Other Cloud Platforms

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/vestara

# Deploy
gcloud run deploy vestara \
  --image gcr.io/PROJECT_ID/vestara \
  --platform managed \
  --port 8501 \
  --allow-unauthenticated
```

### AWS ECS / Fargate

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker build -t vestara .
docker tag vestara ACCOUNT.dkr.ecr.REGION.amazonaws.com/vestara:latest
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/vestara:latest
```

Deploy via ECS task definition with port mapping `8501:8501`.

### Azure Container Apps

```bash
# Build and push to ACR
az acr build --registry myRegistry --image vestara:latest .

# Deploy
az containerapp up \
  --name vestara \
  --image myRegistry.azurecr.io/vestara:latest \
  --port 8501 \
  --environment-id ENVIRONMENT_ID
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `STREAMLIT_SERVER_HEADLESS` | `true` | Run without opening a browser |
| `STREAMLIT_SERVER_RUN_ON_SAVE` | `true` | Reload on file changes |
| `STREAMLIT_SERVER_ENABLE_CORS` | `false` | Disable CORS for security |
| `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION` | `true` | Enable XSRF protection |

Override in `docker-compose.yml` environment section or in the cloud platform's secrets console.

---

## Health Check

Streamlit exposes a health endpoint at `http://localhost:8501/_stcore/health`. Returns `200 OK` when the app is ready.

---

## Troubleshooting

**App won't start?**
```bash
# Check if port 8501 is already in use
lsof -i :8501

# Run Streamlit directly for verbose output
streamlit run src/ui/app.py --server.headless=false
```

**Dependencies missing?**
```bash
# Rebuild from scratch
docker compose down --rmi local
docker compose up --build
```

**Live reload not working?**
Uncomment the `volumes:` block in `docker-compose.yml` to mount source directories.
