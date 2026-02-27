# 🚀 Deployment Guide - AI Crop Disease Detector

Complete guide for deploying the AI Crop Disease Detector to various platforms.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
  - [Render](#render-recommended)
  - [Railway](#railway)
  - [Heroku](#heroku)
  - [AWS EC2](#aws-ec2)
  - [Google Cloud Run](#google-cloud-run)
  - [Azure App Service](#azure-app-service)
- [Production Optimization](#production-optimization)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Git installed and repository cloned
- ✅ Model file (`crop_model.h5`) present in `model/` directory
- ✅ Python 3.12+ installed (for local/manual deployments)
- ✅ Docker installed (for containerized deployments)
- ✅ Cloud platform account (for cloud deployments)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/chetan2007-k/AI-Crop-Disease-Detector.git
cd AI-Crop-Disease-Detector

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run application
python backend/app.py
```

Access at: **http://localhost:5000/frontend/**

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Dockerfile Only

```bash
# Build image
docker build -t crop-disease-detector:latest .

# Run container
docker run -d \
  -p 5000:5000 \
  --name crop-app \
  -v $(pwd)/model:/app/model \
  --restart unless-stopped \
  crop-disease-detector:latest

# View logs
docker logs -f crop-app

# Stop and remove
docker stop crop-app && docker rm crop-app
```

---

## Cloud Platforms

### Render (Recommended)

**Best for**: Quick deployment with free tier

#### Step 1: Create `render.yaml`

```yaml
services:
  - type: web
    name: crop-disease-detector
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 backend.app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.3
      - key: FLASK_ENV
        value: production
```

#### Step 2: Deploy

1. Push code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Render auto-deploys from `render.yaml`

**Access**: `https://your-app-name.onrender.com/frontend/`

---

### Railway

**Best for**: Instant deployment with generous free tier

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT backend.app:app" > Procfile

# Deploy
railway up

# Open in browser
railway open
```

**URL**: Auto-generated (e.g., `your-app-railway.app`)

---

### Heroku

**Best for**: Established platform with Add-ons ecosystem

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create crop-disease-detector-app

# Add Python buildpack
heroku buildpacks:set heroku/python

# Create Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT backend.app:app" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open app
heroku open
```

**Custom Domain**: `heroku domains:add yourdomain.com`

---

### AWS EC2

**Best for**: Full control, scalable infrastructure

#### Step 1: Launch EC2 Instance

1. Go to AWS EC2 Console
2. Launch Ubuntu 24.04 LTS instance (t2.medium recommended)
3. Configure security groups:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
4. Download `.pem` key file

#### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Git
sudo apt install git -y

# Clone repository
git clone https://github.com/chetan2007-k/AI-Crop-Disease-Detector.git
cd AI-Crop-Disease-Detector

# Setup virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

#### Step 3: Setup Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create site configuration
sudo nano /etc/nginx/sites-available/crop-detector
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # or EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/crop-detector /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 4: Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/crop-detector.service
```

**Service Configuration:**
```ini
[Unit]
Description=Crop Disease Detector API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Crop-Disease-Detector
Environment="PATH=/home/ubuntu/AI-Crop-Disease-Detector/.venv/bin"
ExecStart=/home/ubuntu/AI-Crop-Disease-Detector/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 backend.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable crop-detector
sudo systemctl start crop-detector
sudo systemctl status crop-detector
```

#### Step 5: Setup SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is enabled by default
sudo certbot renew --dry-run
```

**Access**: `https://your-domain.com/frontend/`

---

### Google Cloud Run

**Best for**: Serverless, auto-scaling deployment

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/crop-detector

# Deploy
gcloud run deploy crop-detector \
  --image gcr.io/YOUR_PROJECT_ID/crop-detector \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

---

### Azure App Service

**Best for**: Windows integration, enterprise deployments

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name crop-detector-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name crop-detector-plan \
  --resource-group crop-detector-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group crop-detector-rg \
  --plan crop-detector-plan \
  --name crop-disease-detector \
  --runtime "PYTHON:3.12"

# Deploy from GitHub
az webapp deployment source config \
  --name crop-disease-detector \
  --resource-group crop-detector-rg \
  --repo-url https://github.com/chetan2007-k/AI-Crop-Disease-Detector \
  --branch main
```

---

## Production Optimization

### 1. Use Gunicorn with Multiple Workers

```bash
# Production command
gunicorn -w 4 \
  -b 0.0.0.0:5000 \
  --timeout 120 \
  --worker-class sync \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  backend.app:app
```

### 2. Enable Logging

```python
# In backend/app.py
import logging
logging.basicConfig(level=logging.INFO)
```

### 3. Environment Variables

```bash
export FLASK_ENV=production
export MODEL_PATH=/app/model/crop_model.h5
export LOG_LEVEL=INFO
```

### 4. Nginx Caching

```nginx
# Cache static assets
location /frontend/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 5. Database for Logs (Optional)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Setup database for prediction logs
```

---

## Monitoring & Logging

### Health Check Endpoint

```bash
# Test health
curl https://your-domain.com/health
```

Expected: `{"status": "healthy", "model_loaded": true}`

### Log Monitoring

```bash
# View Gunicorn logs
tail -f /var/log/crop-detector/access.log
tail -f /var/log/crop-detector/error.log

# Systemd service logs
sudo journalctl -u crop-detector -f
```

### Uptime Monitoring

Setup monitoring with:
- **UptimeRobot**: Free tier for 50 monitors
- **Pingdom**: Professional monitoring
- **New Relic**: Application performance monitoring

---

## Troubleshooting

### Issue: Model Not Loading

```bash
# Check model file exists
ls -lh model/crop_model.h5

# Verify TensorFlow installation
python -c "import tensorflow as tf; print(tf.__version__)"
```

### Issue: Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Issue: Out of Memory

```bash
# Reduce Gunicorn workers
gunicorn -w 2 backend.app:app  # Instead of -w 4

# Monitor memory
free -h
htop
```

### Issue: Slow Predictions

```bash
# Enable model optimization
# Add to backend/app.py:
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', run_eagerly=False)
```

---

## Security Checklist

- [ ] Use HTTPS (SSL certificate)
- [ ] Set secure environment variables
- [ ] Implement rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Keep dependencies updated
- [ ] Use secrets manager for API keys
- [ ] Enable firewall rules
- [ ] Regular security audits

---

## Cost Estimation

| Platform | Free Tier | Paid Plan |
|----------|-----------|-----------|
| **Render** | 750 hrs/month | $7/month (Starter) |
| **Railway** | $5 credit | $20/month (Hobby) |
| **Heroku** | 550 dyno hrs | $7/month (Eco) |
| **AWS EC2** | 750 hrs/month (t2.micro) | $25/month (t2.medium) |
| **Google Cloud Run** | 2M requests/month | Pay per use |
| **Azure** | $200 credit | $13/month (B1) |

---

## Next Steps

1. Choose deployment platform based on your needs
2. Follow platform-specific steps above
3. Test all endpoints after deployment
4. Setup monitoring and logging
5. Configure custom domain (optional)
6. Enable HTTPS with SSL certificate
7. Share your deployed app! 🚀

---

**Need Help?** Open an issue on [GitHub](https://github.com/chetan2007-k/AI-Crop-Disease-Detector/issues)
