import os
import base64
import time
import sqlite3
from urllib.parse import quote
from config.settings import (
    BASE_DIR, DB_PATH, STATIC_DIR, AVATARS_DIR,
    BANNERS_DIR, UPLOADS_STUDENTS_DIR, UPLOADS_ADMIN_DIR, VIDEOS_DIR
)

# Ensure required directories exist
for d in [STATIC_DIR, AVATARS_DIR, BANNERS_DIR, UPLOADS_STUDENTS_DIR, UPLOADS_ADMIN_DIR, VIDEOS_DIR]:
    os.makedirs(d, exist_ok=True)


def generate_initials_avatar(name="Student", bg_color="#0F172A", text_color="#38BDF8"):
    """Generate a clean SVG data URI with initials."""
    parts = (name or "S").strip().split()
    if len(parts) >= 2:
        initials = parts[0][0].upper() + parts[1][0].upper()
    elif len(parts) == 1 and len(parts[0]) > 0:
        initials = parts[0][0].upper()
    else:
        initials = "S"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
        <rect width="200" height="200" rx="100" fill="{bg_color}" />
        <circle cx="100" cy="100" r="94" fill="none" stroke="{text_color}" stroke-width="4" stroke-opacity="0.4" />
        <text x="50%" y="54%" font-family="Plus Jakarta Sans, system-ui, sans-serif" font-size="76" font-weight="800" 
              fill="{text_color}" text-anchor="middle" dominant-baseline="middle">{initials}</text>
    </svg>"""
    return f"data:image/svg+xml;utf8,{quote(svg)}"


def get_image_data_uri(path_or_url, fallback_name="Student"):
    """
    Convert a local image path or return remote URL as a valid image source
    suitable for HTML <img> or CSS background-image.
    """
    if not path_or_url:
        return generate_initials_avatar(fallback_name)

    path_or_url = str(path_or_url).strip()

    # Remote URL or already data URI
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url

    # Check local path
    full_path = path_or_url
    if not os.path.isabs(full_path):
        full_path = os.path.join(BASE_DIR, path_or_url)

    if os.path.exists(full_path) and os.path.isfile(full_path):
        ext = os.path.splitext(full_path)[1].lower().replace(".", "")
        if ext in ["jpg", "jpeg"]:
            mime = "image/jpeg"
        elif ext == "png":
            mime = "image/png"
        elif ext == "webp":
            mime = "image/webp"
        elif ext == "svg":
            mime = "image/svg+xml"
        else:
            mime = "image/jpeg"

        try:
            with open(full_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{encoded}"
        except Exception:
            return generate_initials_avatar(fallback_name)

    return generate_initials_avatar(fallback_name)


def get_student_photo_uri(student):
    """
    Get the photo data URI for a student.
    Guarantees that EVERY student returns a valid, high quality photo or avatar.
    """
    if not student:
        return generate_initials_avatar("Student")

    student_id = getattr(student, "id", 1) or 1
    name = getattr(student, "name", "Student") or "Student"
    photo_path = getattr(student, "photo", None)

    # 1. Custom uploaded or assigned photo
    if photo_path:
        full_path = photo_path
        if not os.path.isabs(full_path) and not photo_path.startswith(("http://", "https://", "data:")):
            full_path = os.path.join(BASE_DIR, photo_path)
        if photo_path.startswith(("http://", "https://", "data:")) or os.path.exists(full_path):
            return get_image_data_uri(photo_path, fallback_name=name)

    # 2. Local avatar fallback by student ID (avatar_1.jpg to avatar_17.jpg)
    avatar_num = ((student_id - 1) % 17) + 1
    avatar_rel = os.path.join("static", "avatars", f"avatar_{avatar_num}.jpg")
    avatar_abs = os.path.join(BASE_DIR, avatar_rel)

    if os.path.exists(avatar_abs):
        return get_image_data_uri(avatar_rel, fallback_name=name)

    # 3. Clean SVG initials avatar
    return generate_initials_avatar(name)


def save_uploaded_photo(uploaded_file, student_id=None):
    """
    Save an uploaded file to static/uploads/students/ and optionally sync to AWS S3.
    """
    if not uploaded_file:
        return None

    ext = "jpg"
    if hasattr(uploaded_file, "name") and uploaded_file.name:
        parsed_ext = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")
        if parsed_ext in ["jpg", "jpeg", "png", "webp"]:
            ext = parsed_ext

    timestamp = int(time.time())
    sid_str = f"stu_{student_id}" if student_id else "new"
    filename = f"{sid_str}_{timestamp}.{ext}"
    target_abs = os.path.join(UPLOADS_STUDENTS_DIR, filename)

    # Read bytes
    file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    with open(target_abs, "wb") as f:
        f.write(file_bytes)

    rel_path = f"static/uploads/students/{filename}"

    # Background upload to AWS S3 if enabled
    try:
        from utils.aws_utils import upload_file_to_s3
        s3_key = f"uploads/students/{filename}"
        upload_file_to_s3(target_abs, s3_key)
    except Exception:
        pass

    return rel_path


def get_app_background_uri():
    """Get the photographic background data URI for the entire application."""
    rel = os.path.join("static", "banners", "hostel_building.jpg")
    abs_path = os.path.join(BASE_DIR, rel)
    if os.path.exists(abs_path):
        return get_image_data_uri(rel)
    return "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?auto=format&fit=crop&w=1920&q=85"


def get_dashboard_banner_uri():
    """Get the photographic background data URI for the dashboard profile header."""
    rel = os.path.join("static", "banners", "dashboard_banner.jpg")
    abs_path = os.path.join(BASE_DIR, rel)
    if os.path.exists(abs_path):
        return get_image_data_uri(rel)
    return "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?auto=format&fit=crop&w=1600&q=80"


def get_student_banner_uri():
    """Get the photographic background data URI for the student profile cover."""
    rel = os.path.join("static", "banners", "student_banner.jpg")
    abs_path = os.path.join(BASE_DIR, rel)
    if os.path.exists(abs_path):
        return get_image_data_uri(rel)
    return "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1600&q=80"


# =========================================================
# ADMIN PROFILE HELPERS (ARPITA BEHERA)
# =========================================================

def get_admin_profile():
    """Get the current admin profile dictionary from database."""
    default_admin = {
        "id": 1,
        "name": "Arpita Behera",
        "title": "Hostel Administrator & Chief Warden",
        "email": "arpita.behera@hostelhub.edu",
        "phone": "+91 98765 43210",
        "office": "Warden Office, Block A",
        "photo": "static/banners/warden_profile.jpg",
        "status": "Office Online"
    }

    if not os.path.exists(DB_PATH):
        return default_admin

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, name, title, email, phone, office, photo, status FROM admin_profile WHERE id = 1")
        row = cur.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1] or "Arpita Behera",
                "title": row[2] or "Hostel Administrator & Chief Warden",
                "email": row[3] or "arpita.behera@hostelhub.edu",
                "phone": row[4] or "+91 98765 43210",
                "office": row[5] or "Warden Office, Block A",
                "photo": row[6],
                "status": row[7] or "Office Online"
            }
    except Exception:
        pass

    return default_admin


def update_admin_profile(name, title, email, phone, office, photo, status):
    """Update admin profile details in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            UPDATE admin_profile
            SET name = ?, title = ?, email = ?, phone = ?, office = ?, photo = ?, status = ?
            WHERE id = 1
        """, (name, title, email, phone, office, photo, status))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("update_admin_profile error:", e)
        return False


def save_admin_photo(uploaded_file):
    """Save uploaded admin profile photo to static/uploads/admin/ and sync to AWS S3."""
    if not uploaded_file:
        return None

    ext = "jpg"
    if hasattr(uploaded_file, "name") and uploaded_file.name:
        parsed_ext = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")
        if parsed_ext in ["jpg", "jpeg", "png", "webp"]:
            ext = parsed_ext

    timestamp = int(time.time())
    filename = f"admin_arpita_{timestamp}.{ext}"
    target_abs = os.path.join(UPLOADS_ADMIN_DIR, filename)

    file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    with open(target_abs, "wb") as f:
        f.write(file_bytes)

    rel_path = f"static/uploads/admin/{filename}"

    # Sync to S3
    try:
        from utils.aws_utils import upload_file_to_s3
        s3_key = f"uploads/admin/{filename}"
        upload_file_to_s3(target_abs, s3_key)
    except Exception:
        pass

    return rel_path


def get_admin_avatar_uri():
    """
    Get the avatar photo data URI for Arpita Behera.
    If custom photo exists, uses it; if photo removed, generates initials avatar.
    """
    admin = get_admin_profile()
    photo_path = admin.get("photo")
    name = admin.get("name", "Arpita Behera")

    if photo_path:
        full_path = photo_path
        if not os.path.isabs(full_path) and not photo_path.startswith(("http://", "https://", "data:")):
            full_path = os.path.join(BASE_DIR, photo_path)
        if photo_path.startswith(("http://", "https://", "data:")) or os.path.exists(full_path):
            return get_image_data_uri(photo_path, fallback_name=name)

    # Fallback to initials avatar
    return generate_initials_avatar(name, bg_color="#0F172A", text_color="#38BDF8")


def save_uploaded_video(uploaded_file):
    """Save an uploaded tour video file to static/videos/ and sync to AWS S3."""
    if not uploaded_file:
        return None

    ext = "mp4"
    if hasattr(uploaded_file, "name") and uploaded_file.name:
        parsed_ext = os.path.splitext(uploaded_file.name)[1].lower().replace(".", "")
        if parsed_ext in ["mp4", "webm", "mov", "avi", "mkv"]:
            ext = parsed_ext

    timestamp = int(time.time())
    safe_name = f"tour_video_{timestamp}.{ext}"
    target_abs = os.path.join(VIDEOS_DIR, safe_name)

    file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
    with open(target_abs, "wb") as f:
        f.write(file_bytes)

    rel_path = f"static/videos/{safe_name}"

    try:
        from utils.aws_utils import upload_file_to_s3
        s3_key = f"videos/{safe_name}"
        upload_file_to_s3(target_abs, s3_key)
    except Exception:
        pass

    return rel_path
