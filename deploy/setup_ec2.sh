#!/usr/bin/env bash
# =========================================================
# HOSTEL HUB - ONE-CLICK EC2 BOOTSTRAP SCRIPT
# Supports: Ubuntu 22.04 / 24.04 LTS & Amazon Linux 2023
# Optimized for 1 vCPU / 1 GiB RAM instances (t2.micro / t3.micro)
# =========================================================

set -e

echo "🚀 Starting Hostel Hub EC2 Deployment..."

# 1. Determine Project Directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
cd "$APP_DIR" || exit 1
echo "📂 Working directory: $APP_DIR"

# 2. Setup 2GB Swap Space (Essential for 1 GiB RAM instances like t2.micro / t3.micro)
if [ ! -f /swapfile ] && [ "$(free -m | awk '/^Mem:/{print $2}')" -le 1500 ]; then
    echo "🧠 Configuring 2GB Swap Memory for stability on micro instances..."
    sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "✅ 2GB Swap successfully enabled!"
fi

# 3. Detect OS and install prerequisites
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
fi

echo "📦 Detected OS: $OS"

if [ "$OS" = "amzn" ]; then
    echo "Updating Amazon Linux packages..."
    sudo dnf update -y
    sudo dnf install -y git python3.11 python3.11-pip docker
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER" || true
    # Install docker compose plugin if missing
    if ! docker compose version &> /dev/null; then
        echo "Installing Docker Compose plugin..."
        sudo mkdir -p /usr/local/lib/docker/cli-plugins
        sudo curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" -o /usr/local/lib/docker/cli-plugins/docker-compose
        sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    fi
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    echo "Updating Ubuntu packages..."
    sudo apt-get update -y
    sudo apt-get install -y git python3 python3-pip python3-venv docker.io docker-compose-v2 curl
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER" || true
fi

# 4. Ensure correct file permissions for database and uploads
sudo chmod -R 777 "$APP_DIR/static" 2>/dev/null || true
if [ -f "$APP_DIR/hostel_hub.db" ]; then
    sudo chmod 666 "$APP_DIR/hostel_hub.db"
fi

# 5. Launch Application
if command -v docker &> /dev/null && [ -f "$APP_DIR/deploy/docker-compose.yml" ]; then
    echo "🐳 Launching via Docker Compose..."
    # Build and run containers
    sudo docker compose -f "$APP_DIR/deploy/docker-compose.yml" up -d --build
    echo "✅ Docker containers launched successfully!"
else
    # Fallback: Native Python Virtual Environment & Systemd
    echo "🐍 Setting up Python Virtual Environment..."
    python3 -m venv "$APP_DIR/venv"
    "$APP_DIR/venv/bin/pip" install --upgrade pip
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

    echo "⚙️ Configuring Systemd Service..."
    cat <<EOF | sudo tee /etc/systemd/system/hostelhub.service
[Unit]
Description=Hostel Hub Streamlit Web Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.enableCORS false --server.enableXsrfProtection false
Restart=always
RestartSec=5
Environment=PATH=$APP_DIR/venv/bin:/usr/bin:/bin
Environment=STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable --now hostelhub
    echo "✅ Hostel Hub systemd service active!"
fi

# 6. Fetch and Output Public IP
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
