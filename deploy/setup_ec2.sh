#!/usr/bin/env bash
# =========================================================
# HOSTEL HUB - ONE-CLICK EC2 BOOTSTRAP SCRIPT
# Supports: Amazon Linux 2023 & Ubuntu 22.04 / 24.04 LTS
# =========================================================

set -e

echo "🚀 Starting Hostel Hub EC2 Deployment..."

# 1. Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo "📦 Detected OS: $OS"

# 2. Update packages and install prerequisites
if [ "$OS" = "amzn" ]; then
    echo "Updating Amazon Linux packages..."
    sudo dnf update -y
    sudo dnf install -y git python3.11 python3.11-pip docker
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Updating Ubuntu packages..."
    sudo apt-get update -y && sudo apt-get upgrade -y
    sudo apt-get install -y git python3 python3-pip python3-venv docker.io docker-compose-v2
    sudo systemctl enable --now docker
    sudo usermod -aG docker $USER
fi

# 3. Project Directory Setup
APP_DIR="$HOME/hostel_hub"
if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repository..."
    # Replace with your repository URL if deploying from Git
    # git clone <YOUR_REPO_URL> "$APP_DIR"
fi

cd "$APP_DIR" || exit 1

# 4. Launch Option A: Docker Compose (Recommended)
if command -v docker &> /dev/null && [ -f "deploy/docker-compose.yml" ]; then
    echo "🐳 Launching via Docker Compose..."
    sudo docker compose -f deploy/docker-compose.yml up -d --build
    echo "✅ Docker containers launched successfully!"
else
    # Launch Option B: Native Python Virtual Environment & Systemd
    echo "🐍 Setting up Python Virtual Environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    echo "⚙️ Configuring Systemd Service..."
    sudo cp deploy/hostelhub.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now hostelhub
    echo "✅ Hostel Hub systemd service active!"
fi

# 5. Output Public IP
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null || true)
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" "http://169.254.169.254/latest/meta-data/public-ipv4" 2>/dev/null || curl -s ifconfig.me)

echo ""
echo "========================================================="
echo "🎉 HOSTEL HUB IS DEPLOYED & LIVE ON EC2!"
echo "Access in your web browser:"
echo "👉 http://${PUBLIC_IP}:8501   (Direct Streamlit Port)"
echo "👉 http://${PUBLIC_IP}        (Nginx Reverse Proxy)"
echo "========================================================="
echo "Ensure EC2 Security Group allows Inbound TCP on ports 8501 and 80!"
