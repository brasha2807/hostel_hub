import os
import sqlite3
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "hostel_hub.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.replace(os.sep, '/')}")

is_sqlite = DATABASE_URL.startswith("sqlite")

engine_args = {}
if is_sqlite:
    engine_args["connect_args"] = {"check_same_thread": False, "timeout": 30}

engine = create_engine(DATABASE_URL, **engine_args)

# Enable WAL mode and foreign keys for SQLite performance & concurrency
if is_sqlite:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
        except Exception:
            pass
        finally:
            cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

Base = declarative_base()


def init_db():
    """Ensure database schema includes all tables, columns, migrations, and initial data."""
    try:
        # Import models so Base.metadata knows about them
        from models.student import Student
        from models.room import Room
        from models.attendance import Attendance
        from models.visitor import Visitor
        from models.gate_pass import GatePass
        from models.complaint import Complaint
        from models.notice import Notice
        from models.admin_profile import AdminProfile
        from models.hostel_video import HostelVideo
        from models.user import User

        Base.metadata.create_all(bind=engine)

        if is_sqlite and os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # 1. Ensure students table has 'photo' and 'room_number' columns
            cur.execute("PRAGMA table_info(students)")
            cols = [c[1] for c in cur.fetchall()]
            if cols:
                if "photo" not in cols:
                    cur.execute("ALTER TABLE students ADD COLUMN photo VARCHAR")
                    conn.commit()
                if "room_number" not in cols:
                    cur.execute("ALTER TABLE students ADD COLUMN room_number VARCHAR")
                    conn.commit()

            # 2. Ensure admin_profile table exists and has initial record
            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_profile (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    office TEXT NOT NULL,
                    photo TEXT,
                    status TEXT NOT NULL
                )
            """)
            cur.execute("SELECT COUNT(*) FROM admin_profile")
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    INSERT INTO admin_profile (id, name, title, email, phone, office, photo, status)
                    VALUES (1, 'Arpita Behera', 'Hostel Administrator & Chief Warden',
                            'arpita.behera@hostelhub.edu', '+91 98765 43210',
                            'Warden Office, Block A', 'static/banners/warden_profile.jpg', 'Office Online')
                """)
                conn.commit()

            # 3. Ensure hostel_videos table exists and has tour videos
            cur.execute("""
                CREATE TABLE IF NOT EXISTS hostel_videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    description TEXT,
                    room_capacity TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            cur.execute("SELECT COUNT(*) FROM hostel_videos")
            if cur.fetchone()[0] == 0:
                initial_videos = [
                    (
                        "Hostel Campus & Main Entrance Tour",
                        "Exterior & Campus",
                        "https://www.youtube.com/watch?v=ScMzIvxBSi4",
                        "Comprehensive walkthrough of the modern hostel buildings, residential blocks A & B, secure entrance gates, landscaped courtyards, and campus surroundings.",
                        "Blocks A & B • 18 Rooms Total",
                        "2026-10-21"
                    ),
                    (
                        "Student Rooms & Bed Capacity Walkthrough",
                        "Student Rooms",
                        "https://www.youtube.com/watch?v=8Z1eMy2FoGY",
                        "Inside look at spacious student accommodation. Features 2-bed and 4-bed study setups, ergonomically designed study tables, personal wardrobes, attached washrooms, and natural ventilation.",
                        "Double & Quad Sharing (2 to 4 Beds / Room)",
                        "2026-10-21"
                    ),
                    (
                        "Interior Common Room & Study Lounge",
                        "Interior & Living",
                        "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
                        "Tour of indoor air-conditioned reading halls, high-speed Wi-Fi study lounges, recreational game zones, and elevator access across all floors.",
                        "Capacity: 120 Students in Study Lounge",
                        "2026-10-21"
                    ),
                    (
                        "Dining Mess, Gym & Hostel Facilities",
                        "Hostel Facilities",
                        "https://www.w3schools.com/html/mov_bbb.mp4",
                        "Walkthrough of the modern hygienic student dining mess serving 4 meals daily, fitness gym, laundry facility, RO drinking water stations, and 24/7 CCTV security desk.",
                        "Dining Hall Capacity: 250 Students / Batch",
                        "2026-10-21"
                    )
                ]
                cur.executemany("""
                    INSERT INTO hostel_videos (title, category, video_url, description, room_capacity, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, initial_videos)
                conn.commit()

            conn.close()
    except Exception as e:
        print(f"[Init DB] Warning: {e}")


def get_db():
    """Get a raw SessionLocal instance. Remember to close in finally block!"""
    init_db()
    return SessionLocal()


@contextmanager
def get_db_session():
    """Context manager for safe SQLAlchemy session execution with auto-commit/rollback."""
    init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
