# 🌐 AWS EC2 Deployment Guide: Hostel Hub (Luxe Edition)

This guide provides end-to-end instructions for deploying the **Hostel Hub** application on an Amazon Elastic Compute Cloud (**AWS EC2**) instance with Docker, Nginx reverse proxy, automatic system reboot survival, and Amazon S3 cloud asset sync.

---

## 🏛️ Architecture Overview

```text
       [ Clients / Browsers ]
                 │
                 ▼ (Port 80 / 443 HTTPS)
      ┌─────────────────────────┐
      │   AWS EC2 (Ubuntu / AL) │
      │  ┌───────────────────┐  │
      │  │    Nginx Proxy    │  │ (Port 8501)
      │  └────────┬──────────┘  │
      │           ▼             │
      │  ┌───────────────────┐  │        ┌─────────────────────────┐
      │  │ Hostel Hub App    │──┼───────▶│ Amazon S3 Storage       │
      │  │ (Streamlit Py3.12)│  │ Sync   │ hostelhub-media-*       │
      │  └────────┬──────────┘  │        │ (Photos, Videos, Backups)
      │           ▼             │        └─────────────────────────┘
      │  ┌───────────────────┐  │
      │  │ SQLite DB / RDS   │  │
      │  └───────────────────┘  │
      └─────────────────────────┘
```

---

## 📋 Step 1: Launch an AWS EC2 Instance

1. Log into your **AWS Management Console** and select region **Asia Pacific (Mumbai) `ap-south-1`** (or your preferred region).
2. Navigate to **EC2** ➔ Click **Launch Instance**.
3. **Name**: `hostel-hub-production`
4. **OS Image (AMI)**: Select **Ubuntu 24.04 LTS (HVM)** or **Amazon Linux 2023**.
5. **Instance Type**:
   - **Recommended**: `t3.small` (2 vCPU, 2 GiB RAM) — Ideal for smooth video streaming and concurrent student portals.
   - **Free-Tier Eligible**: `t2.micro` or `t3.micro` (1 GiB RAM) — Works well with swap enabled.
6. **Key Pair**: Select or create an SSH key pair (e.g. `hostelhub-key.pem`) and download it.
7. **Network Settings / Security Group**:
   Create a new Security Group with the following inbound rules:
   | Type | Protocol | Port Range | Source | Description |
   | :--- | :--- | :--- | :--- | :--- |
   | **SSH** | TCP | `22` | `My IP` (or `0.0.0.0/0`) | Secure Terminal Access |
   | **HTTP** | TCP | `80` | `0.0.0.0/0` | Web Access via Nginx |
   | **HTTPS** | TCP | `443` | `0.0.0.0/0` | Secure Web Access (SSL) |
   | **Custom TCP** | TCP | `8501` | `0.0.0.0/0` | Direct Streamlit Access |
8. **Storage**: Configure **20 GiB gp3 SSD** to accommodate media uploads and database growth.
9. Click **Launch Instance**.

---

## 🛡️ Step 2: Attach an IAM Role for Amazon S3 Access

To allow your EC2 instance to upload student photos, videos, and database backups to Amazon S3 without hardcoding API keys:

1. In the AWS Console, navigate to **IAM** ➔ **Roles** ➔ **Create Role**.
2. Select **AWS Service** ➔ **EC2**.
3. Attach Policy: `AmazonS3FullAccess` (or create a scoped policy for bucket `hostelhub-media-474333173964`).
4. Name the role: `HostelHub-EC2-S3Role` ➔ Click **Create Role**.
5. Go back to **EC2 Console** ➔ Select your running instance ➔ **Actions** ➔ **Security** ➔ **Modify IAM Role**.
6. Select `HostelHub-EC2-S3Role` and click **Update IAM Role**.

---

## 💻 Step 3: Connect to your EC2 Instance

Open PowerShell or Terminal on your local machine:

```powershell
# Set correct permissions on your key pair
chmod 400 hostelhub-key.pem

# SSH into the EC2 instance (replace with your EC2 Public IP)
ssh -i "hostelhub-key.pem" ubuntu@<YOUR-EC2-PUBLIC-IP>
```

---

## 🚀 Step 4: Deploy Hostel Hub (One-Command Automated)

Once inside your EC2 terminal, run:

```bash
# 1. Clone the repository or copy project files
git clone <YOUR_GIT_REPO_URL> ~/hostel_hub
cd ~/hostel_hub

# 2. Make the deployment script executable and run it
chmod +x deploy/setup_ec2.sh
./deploy/setup_ec2.sh
```

### Alternatively, Deploy Manually via Docker Compose:

```bash
# 1. Install Docker & Docker Compose
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# 2. Launch Containers
cd ~/hostel_hub
sudo docker compose -f deploy/docker-compose.yml up -d --build

# 3. View live logs
sudo docker compose -f deploy/docker-compose.yml logs -f
```

---

## 🌐 Step 5: Access Your Live Application

Your application is now live on the internet! Open your web browser and visit:

- Direct Streamlit: **`http://<YOUR-EC2-PUBLIC-IP>:8501`**
- Nginx Reverse Proxy: **`http://<YOUR-EC2-PUBLIC-IP>`**

---

## 🔒 Step 6: (Optional) Setup Custom Domain & Free SSL (HTTPS)

To connect a custom domain (e.g. `hostel.yourcollege.edu`) with free automated SSL certificates via Let's Encrypt:

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL Certificate
sudo certbot --nginx -d hostel.yourcollege.edu
```

Certbot will automatically configure HTTPS on port 443 and setup auto-renewal!

---

## 💾 Step 7: Automated Nightly Database Backups to Amazon S3

Hostel Hub includes built-in S3 backup tools. To schedule an automatic daily database snapshot to your AWS S3 bucket:

```bash
# Open crontab
crontab -e

# Add this line to run backup every midnight at 00:00:
0 0 * * * cd /home/ubuntu/hostel_hub && ./venv/bin/python -c "from utils.aws_utils import backup_database_to_s3; backup_database_to_s3()" >> /var/log/hostelhub_backup.log 2>&1
```

---

## 🛠️ Verification & Troubleshooting Checklist

| Check | Command | Expected Result |
| :--- | :--- | :--- |
| **Streamlit Health** | `curl http://localhost:8501/_stcore/health` | Returns `ok` |
| **Docker Status** | `sudo docker ps` | Containers `hostelhub_app` & `hostelhub_nginx` show status `Up` |
| **AWS Credentials** | `aws sts get-caller-identity` | Returns Account `474333173964` |
| **S3 Connectivity** | Inside app ➔ Open **AWS Cloud & Storage** tab | Shows green `🟢 AWS Connected` badge |
