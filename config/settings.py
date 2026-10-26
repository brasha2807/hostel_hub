import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "hostel_hub.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.replace(os.sep, '/')}")

STATIC_DIR = os.path.join(BASE_DIR, "static")
AVATARS_DIR = os.path.join(STATIC_DIR, "avatars")
BANNERS_DIR = os.path.join(STATIC_DIR, "banners")
UPLOADS_STUDENTS_DIR = os.path.join(STATIC_DIR, "uploads", "students")
UPLOADS_ADMIN_DIR = os.path.join(STATIC_DIR, "uploads", "admin")
VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")

# Ensure all essential directories exist
for folder in [STATIC_DIR, AVATARS_DIR, BANNERS_DIR, UPLOADS_STUDENTS_DIR, UPLOADS_ADMIN_DIR, VIDEOS_DIR]:
    os.makedirs(folder, exist_ok=True)

APP_TITLE = "Hostel Hub"
APP_SUBTITLE = "College Hostel Management System"
APP_VERSION = "2.4.0 (Cloud & EC2 Ready)"
DEFAULT_ADMIN_NAME = "Arpita Behera"
DEFAULT_ADMIN_TITLE = "Hostel Administrator & Chief Warden"

MODULES = [
    "Dashboard",
    "Hostel Tour Videos",
    "Student Registration",
    "Student Profile",
    "Room Management",
    "Room Allocation",
    "Attendance",
    "Parent / Visitor",
    "Student Gate Pass",
    "Complaints",
    "Notice Board",
    "AWS Cloud & Storage"
]
