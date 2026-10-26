# 🏨 Hostel Hub — College Hostel Management System (Luxe Edition)

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20EC2%20%7C%20ap--south--1-orange.svg)](https://aws.amazon.com/)
[![Design](https://img.shields.io/badge/Awwwards-Luxe%20Design-00F5D4.svg)](#design-aesthetics)

An enterprise-grade, **Awwwards-level designed** College Hostel Management System engineered with Python, Streamlit, SQLAlchemy, Plotly, and Amazon Web Services (AWS S3 & EC2).

---

## ✨ Features & Modules

1. **Executive Dashboard**: Awwwards luxury glassmorphism design, real-time time-of-day greetings, chief warden profile card, live KPI telemetry, and interactive Plotly analytics (Bed Occupancy donut & Department demographics).
2. **Hostel Tour Videos**: Categorized virtual video walkthroughs (Exterior, Student Dorms, Mess, Gym, Lounges) with direct URL & local video upload support.
3. **Student Registration**: Streamlined resident enrollment with validation, academic details, and portrait photo capture (file upload & webcam).
4. **Student Profile**: Centered high-res portraits, full-resolution zoom inspection tool, webcam snapshot capture, preset avatar library (#1–#17), multi-tab dossier, and safe deletion.
5. **Room Management**: Define hostel blocks, floors, room numbers, and bed capacities with real-time occupancy tracking.
6. **Room Allocation**: Assign resident students to vacant beds, inspect occupants per room, and process resident check-outs.
7. **Attendance**: Daily biometric/manual attendance logging, present/absent audit logs, and date-filtered telemetry.
8. **Parent / Visitor**: Log guest check-in, relation, contact details, entry/exit timestamps, and visit purpose.
9. **Student Gate Pass**: Digital movement pass issuing, reason tracking, and 1-click student return check-in.
10. **Complaints**: Student grievance tickets with category tagging and real-time status progression (Pending ➔ In Progress ➔ Resolved).
11. **Notice Board**: Official broadcast feed with category highlights (Important, General, Fee, Maintenance).
12. **AWS Cloud & Storage**: Live AWS STS verification, Amazon S3 bucket management, 1-click media asset synchronization, database cloud backup, and EC2 instance telemetry.

---

## 🗂️ Clean Modular Folder Structure

```text
hostel_hub/
├── app.py                      # Main entrypoint, theme controller & router
├── config/                     # Application configurations
│   ├── settings.py             # Global constants, paths, module registry
│   └── aws_config.py           # AWS session, region & boto3 client factories
├── database/                   # Database engine & session management
│   └── database.py             # SQLite WAL mode engine, auto-migrations & get_db_session
├── models/                     # Clean SQLAlchemy ORM models
│   ├── student.py              # Student model (includes room_number)
│   ├── room.py                 # Room model (capacity, occupied)
│   ├── attendance.py           # Daily attendance logs
│   ├── visitor.py              # Parent / guest check-in logs
│   ├── gate_pass.py            # Digital gate pass movements
│   ├── complaint.py            # Grievance & repair tickets
│   ├── notice.py               # Broadcast notices
│   ├── admin_profile.py        # Administrator / Warden profile
│   └── hostel_video.py         # Virtual tour videos
├── views/                      # Modular view controllers
│   ├── dashboard.py            # Executive KPI Dashboard & Plotly charts
│   ├── tour_videos.py          # Virtual tour video gallery
│   ├── students.py             # Student registration & profile dossier
│   ├── rooms.py                # Room management & bed allocations
│   ├── attendance.py           # Attendance recording & audits
│   ├── visitors.py             # Visitor registers
│   ├── gate_pass.py            # Gate pass management
│   ├── complaints.py           # Grievance tracker & status updater
│   ├── notices.py              # Notice broadcasts
│   └── aws_monitor.py          # AWS Cloud, S3 & EC2 monitor
├── utils/                      # Helper utilities
│   ├── photo_utils.py          # High-res portraits, avatars, banners & S3 sync
│   ├── aws_utils.py            # STS caller identity, S3 uploads, DB backups
│   └── ui_components.py        # Awwwards design system, CSS injection & Plotly theme
├── static/                     # Media & asset directories
│   ├── avatars/                # Preset avatar portraits (#1–#17)
│   ├── banners/                # Campus & hostel photographic banners
│   ├── uploads/                # Custom uploaded student & admin photos
│   └── videos/                 # Campus tour video clips
├── deploy/                     # Production AWS EC2 deployment suite
│   ├── Dockerfile              # Hardened multi-stage container
│   ├── docker-compose.yml      # Orchestrated Compose configuration
│   ├── nginx.conf              # Reverse proxy with WebSocket upgrade
│   ├── hostelhub.service       # Linux systemd service unit
│   └── setup_ec2.sh            # Automated EC2 bootstrap script
├── .env.example                # Environment variables template
├── requirements.txt            # Dependency manifest
└── EC2_DEPLOYMENT_GUIDE.md     # Step-by-step production deployment manual
```

---

## 🚀 Quickstart (Local Development)

```bash
# 1. Clone repository
git clone <REPO_URL>
cd hostel_hub

# 2. Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Hostel Hub
streamlit run app.py
```

The application will be live at `http://localhost:8501`.

---

## ☁️ AWS Cloud Integration

- **Region**: `ap-south-1` (Mumbai)
- **AWS STS**: Live IAM Identity validation (`474333173964`)
- **S3 Bucket**: `hostelhub-media-474333173964`
- **1-Click Sync**: Upload local photos and videos directly to AWS S3 from the **AWS Cloud & Storage** tab.
- **Disaster Recovery**: 1-click snapshot of `hostel_hub.db` backed up to AWS S3.

For comprehensive cloud deployment on EC2 instances, see [EC2_DEPLOYMENT_GUIDE.md](file:///c:/Users/Arpita/hostel_hub/EC2_DEPLOYMENT_GUIDE.md).
