import streamlit as st
import os
import time as pytime
from datetime import date
from database.database import get_db_session
from models.hostel_video import HostelVideo
from utils import photo_utils


def render_tour_videos():
    st.title("🎥 Virtual Hostel Tour & Facility Showcase")
    st.caption("Immersive video walkthroughs of residential blocks A & B, student dorms, dining mess, study lounges, and campus amenities.")

    # Fetch videos using SQLAlchemy
    with get_db_session() as db:
        video_objs = db.query(HostelVideo).order_by(HostelVideo.id.asc()).all()
        # Convert to list of dicts for safe disconnected rendering
        video_rows = [
            {
                "id": v.id,
                "title": v.title,
                "category": v.category,
                "video_url": v.video_url,
                "description": v.description or "",
                "room_capacity": v.room_capacity or "Standard",
                "created_at": v.created_at
            }
            for v in video_objs
        ]

    # Category Filtering
    categories = ["All Videos", "Exterior & Campus", "Student Rooms", "Interior & Living", "Hostel Facilities"]
    selected_tab = st.radio("Filter Gallery by Category", categories, horizontal=True, key="video_filter_tab")

    filtered_videos = video_rows
    if selected_tab != "All Videos":
        filtered_videos = [v for v in video_rows if v["category"] == selected_tab]

    st.markdown(f"**Displaying {len(filtered_videos)} of {len(video_rows)} showcase videos**")

    # Display Videos in 2-Column Grid
    for v_idx in range(0, len(filtered_videos), 2):
        row_cols = st.columns(2)
        for offset, v in enumerate(filtered_videos[v_idx:v_idx + 2]):
            with row_cols[offset]:
                with st.container(border=True):
                    # Header badges
                    st.markdown(f"""
                    <div style="margin-bottom: 8px; display: flex; gap: 8px; flex-wrap: wrap;">
                        <span class="pill-badge pill-info">🏷️ {v['category']}</span>
                        <span class="pill-badge pill-success">🛏️ {v['room_capacity']}</span>
                    </div>
                    <h3 style="margin: 4px 0 10px 0; color: #FFFFFF !important; font-size: 20px;">{v['title']}</h3>
                    <p style="color: #94A3B8; font-size: 13px; line-height: 1.5; min-height: 40px;">{v['description']}</p>
                    """, unsafe_allow_html=True)

                    # Video Player
                    try:
                        v_url = v["video_url"]
                        if v_url.startswith("static/"):
                            full_path = os.path.join(photo_utils.BASE_DIR, v_url)
                            if os.path.exists(full_path):
                                st.video(full_path)
                            else:
                                st.video(v_url)
                        else:
                            st.video(v_url)
                    except Exception as err:
                        st.error(f"Playback error: {err}")

                    # Manage / Delete Expander
                    with st.expander(f"⚙️ Video Options (#{v['id']})", expanded=False):
                        if st.button(f"🗑️ Delete Video: {v['title']}", key=f"del_vid_btn_{v['id']}"):
                            try:
                                with get_db_session() as db:
                                    target = db.query(HostelVideo).filter(HostelVideo.id == v['id']).first()
                                    if target:
                                        db.delete(target)
                                st.success("Video deleted successfully!")
                                pytime.sleep(0.4)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error removing video: {e}")

    # =========================================================
    # UPLOAD & ADD NEW VIDEO
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("➕ Upload & Add New Facility Video", expanded=False):
        st.subheader("Add Video to Virtual Tour Gallery")
        st.caption("Upload a video file from your computer (.mp4, .webm, .mov) or enter a direct URL / YouTube link.")

        with st.form("add_new_video_form"):
            new_title = st.text_input("Video Title", placeholder="e.g. Deluxe Double Room & Balcony Tour")
            c1, c2 = st.columns(2)
            with c1:
                new_cat = st.selectbox(
                    "Category",
                    ["Exterior & Campus", "Student Rooms", "Interior & Living", "Hostel Facilities", "General Tour"]
                )
            with c2:
                new_cap = st.text_input("Room Capacity / Facility Scope", placeholder="e.g. 2 Beds / Room or Block B 4-Bed Quad")

            new_desc = st.text_area("Video Description", placeholder="Highlights of room ventilation, personal wardrobes, study desks, amenities...")

            st.markdown("##### Video Media Source")
            uploaded_vid = st.file_uploader("Upload Video File (.mp4, .webm, .mov)", type=["mp4", "webm", "mov", "avi", "mkv"])
            new_link = st.text_input("Or Enter Video Link / YouTube URL", placeholder="https://www.youtube.com/watch?v=... or https://.../video.mp4")

            submit_btn = st.form_submit_button("Upload & Save Video", type="primary")

        if submit_btn:
            if not new_title.strip():
                st.error("Please provide a video title.")
            elif not uploaded_vid and not new_link.strip():
                st.error("Please either upload a video file or enter a valid URL.")
            else:
                final_url = ""
                if uploaded_vid:
                    final_url = photo_utils.save_uploaded_video(uploaded_vid)
                else:
                    final_url = new_link.strip()

                try:
                    with get_db_session() as db:
                        new_video = HostelVideo(
                            title=new_title.strip(),
                            category=new_cat,
                            video_url=final_url,
                            description=new_desc.strip(),
                            room_capacity=new_cap.strip() if new_cap.strip() else "Standard",
                            created_at=str(date.today())
                        )
                        db.add(new_video)
                    st.success("✅ Video successfully added to the tour gallery!")
                    pytime.sleep(0.4)
                    st.rerun()
                except Exception as ex:
                    st.error(f"Failed to save video: {ex}")
