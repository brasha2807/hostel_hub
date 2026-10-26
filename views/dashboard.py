import streamlit as st
from datetime import datetime, date
import time as pytime
import plotly.graph_objects as go
import plotly.express as px

from database.database import get_db_session
from models import Student, Room, Attendance, Visitor, GatePass, Complaint, Notice
from utils import photo_utils
from utils.ui_components import get_plotly_dark_theme


def render_dashboard(navigate_fn):
    dash_banner = photo_utils.get_dashboard_banner_uri()
    admin_info = photo_utils.get_admin_profile()
    admin_avatar = photo_utils.get_admin_avatar_uri()

    # Dynamic time-of-day greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
        greet_icon = "🌅"
    elif current_hour < 17:
        greeting = "Good Afternoon"
        greet_icon = "☀️"
    else:
        greeting = "Good Evening"
        greet_icon = "🌙"

    # =========================================================
    # AWWWARDS EXECUTIVE HERO BANNER
    # =========================================================
    st.markdown(f"""
    <div class="aww-hero" style="
        background: linear-gradient(135deg, rgba(8, 13, 26, 0.88) 0%, rgba(15, 23, 42, 0.75) 50%, rgba(30, 41, 59, 0.85) 100%),
                    url('{dash_banner}');
        background-size: cover;
        background-position: center;
    ">
        <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 28px;">
            <div style="flex: 1; min-width: 320px;">
                <div class="aww-hero-badge">
                    <span class="radar-dot"></span> COLLEGE HOSTEL SYSTEM · AWWWARDS LUXE EDITION
                </div>
                <h1 style="margin: 10px 0 12px 0; font-size: 40px; color: #FFFFFF !important; line-height: 1.15; font-weight: 850;">
                    {greeting}, {admin_info['name']} {greet_icon}
                </h1>
                <p style="color: #CBD5E1 !important; font-size: 15px; line-height: 1.6; margin-bottom: 20px; max-width: 660px;">
                    Unified campus residence orchestration: monitor resident students, manage bed allocations, audit visitor logs, track digital gate passes, and resolve facility inquiries in real-time.
                </p>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <span class="pill-badge pill-info">🏛️ Blocks A &amp; B Residential Hall</span>
                    <span class="pill-badge pill-success">📅 Academic Year 2026–27</span>
                    <span class="pill-badge pill-warning">⚡ Cloud Native &amp; EC2 Ready</span>
                </div>
            </div>
            <div style="
                background: rgba(15, 23, 42, 0.80);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-radius: 20px;
                padding: 22px 26px;
                display: flex;
                align-items: center;
                gap: 18px;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
            ">
                <img src="{admin_avatar}" style="
                    width: 76px;
                    height: 76px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 3px solid #38BDF8;
                    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
                " alt="Admin Profile">
                <div>
                    <div style="color: #38BDF8; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase;">
                        Hostel Administration
                    </div>
                    <div style="font-size: 21px; font-weight: 850; color: #FFFFFF; margin: 3px 0;">
                        {admin_info['name']}
                    </div>
                    <div style="color: #94A3B8; font-size: 13px;">
                        {admin_info['title']}
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="radar-dot"></span>
                        <span style="font-size: 12px; color: #34D399; font-weight: 700;">{admin_info['status']}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================
    # ADMIN PROFILE SETTINGS (EXPANDABLE)
    # =========================================================
    with st.expander(f"⚙️ Administrator Profile Settings ({admin_info['name']} · Photo & Details)", expanded=False):
        st.subheader("👤 Chief Warden & Admin Profile")
        st.caption("Update your administrator display name, designation, contact numbers, or manage profile photo.")

        col_adm_left, col_adm_right = st.columns([1, 2])

        with col_adm_left:
            st.markdown("##### Profile Picture")
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 14px;">
                <img src="{admin_avatar}" style="width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: 4px solid #38BDF8; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">
            </div>
            """, unsafe_allow_html=True)

            adm_photo_file = st.file_uploader(
                "Upload New Photo (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                key="admin_photo_upload_dash"
            )

            if st.button("🗑️ Remove Photo (Reset to Initials)", key="btn_remove_adm_photo", use_container_width=True):
                photo_utils.update_admin_profile(
                    admin_info["name"], admin_info["title"], admin_info["email"],
                    admin_info["phone"], admin_info["office"], None, admin_info["status"]
                )
                st.success("Profile photo reset! Initials avatar applied.")
                pytime.sleep(0.4)
                st.rerun()

        with col_adm_right:
            st.markdown("##### Contact & Status Details")
            adm_name_val = st.text_input("Administrator Full Name", value=admin_info["name"], key="edit_adm_name")
            adm_title_val = st.text_input("Designation / Title", value=admin_info["title"], key="edit_adm_title")

            c_email, c_phone = st.columns(2)
            with c_email:
                adm_email_val = st.text_input("Email Address", value=admin_info["email"], key="edit_adm_email")
            with c_phone:
                adm_phone_val = st.text_input("Phone Number", value=admin_info["phone"], key="edit_adm_phone")

            c_off, c_stat = st.columns(2)
            with c_off:
                adm_off_val = st.text_input("Office Location", value=admin_info["office"], key="edit_adm_office")
            with c_stat:
                status_options = ["Office Online", "In Meeting", "Available on Call", "Out of Office"]
                curr_status_idx = status_options.index(admin_info["status"]) if admin_info["status"] in status_options else 0
                adm_stat_val = st.selectbox("Office Availability Status", status_options, index=curr_status_idx, key="edit_adm_status")

            if st.button("💾 Save Profile Changes", type="primary", key="save_adm_profile_btn"):
                new_adm_photo = admin_info["photo"]
                if adm_photo_file:
                    new_adm_photo = photo_utils.save_admin_photo(adm_photo_file)

                saved = photo_utils.update_admin_profile(
                    adm_name_val.strip(),
                    adm_title_val.strip(),
                    adm_email_val.strip(),
                    adm_phone_val.strip(),
                    adm_off_val.strip(),
                    new_adm_photo,
                    adm_stat_val
                )
                if saved:
                    st.success("✅ Profile updated successfully!")
                    pytime.sleep(0.4)
                    st.rerun()
                else:
                    st.error("Failed to update profile.")

    # =========================================================
    # METRICS OVERVIEW
    # =========================================================
    with get_db_session() as db:
        total_students = db.query(Student).count()
        rooms = db.query(Room).all()
        total_rooms = len(rooms)
        total_capacity = sum(getattr(r, "capacity", 0) or 0 for r in rooms)
        occupied_beds = sum(getattr(r, "occupied", 0) or 0 for r in rooms)
        available_beds = max(0, total_capacity - occupied_beds)

        total_attendance = db.query(Attendance).count()
        total_visitors = db.query(Visitor).count()
        total_gate_passes = db.query(GatePass).count()
        total_complaints = db.query(Complaint).count()
        pending_complaints = db.query(Complaint).filter(Complaint.status == "Pending").count()
        total_notices = db.query(Notice).count()

        # Department distribution query for chart
        student_courses = {}
        for s in db.query(Student.course).all():
            c = s[0] or "General"
            student_courses[c] = student_courses.get(c, 0) + 1

    st.markdown("### 📊 Executive Hostel Analytics")
    st.caption("Real-time telemetry and residency figures · Updated live from SQLite / RDS")

    # Row 1 Stat Tiles
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">👨‍🎓 Total Students</div>
            <div class="stat-tile-value">{total_students}</div>
            <div class="stat-tile-sub"><span style="color:#34D399;">● Registered</span> in campus</div>
        </div>
        """, unsafe_allow_html=True)
    with r1_c2:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">🏠 Hostel Rooms</div>
            <div class="stat-tile-value">{total_rooms}</div>
            <div class="stat-tile-sub">Blocks A &amp; B</div>
        </div>
        """, unsafe_allow_html=True)
    with r1_c3:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">🛏️ Total Capacity</div>
            <div class="stat-tile-value">{total_capacity}</div>
            <div class="stat-tile-sub">Max institutional beds</div>
        </div>
        """, unsafe_allow_html=True)
    with r1_c4:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">🔑 Occupied Beds</div>
            <div class="stat-tile-value">{occupied_beds}</div>
            <div class="stat-tile-sub"><span style="color:#38BDF8;">● Active</span> residents</div>
        </div>
        """, unsafe_allow_html=True)

    # Row 2 Stat Tiles
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">✅ Available Beds</div>
            <div class="stat-tile-value" style="color:#34D399;">{available_beds}</div>
            <div class="stat-tile-sub">Ready for allocation</div>
        </div>
        """, unsafe_allow_html=True)
    with r2_c2:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">📋 Attendance Logs</div>
            <div class="stat-tile-value">{total_attendance}</div>
            <div class="stat-tile-sub">Records on file</div>
        </div>
        """, unsafe_allow_html=True)
    with r2_c3:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">👨‍👩‍👧 Visitor Logs</div>
            <div class="stat-tile-value">{total_visitors}</div>
            <div class="stat-tile-sub">Parent / guest check-ins</div>
        </div>
        """, unsafe_allow_html=True)
    with r2_c4:
        st.markdown(f"""
        <div class="stat-tile">
            <div class="stat-tile-label">🚪 Gate Passes</div>
            <div class="stat-tile-value">{total_gate_passes}</div>
            <div class="stat-tile-sub">Transit requests logged</div>
        </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # AWWWARDS INTERACTIVE PLOTLY VISUALIZATIONS
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    col_chart_1, col_chart_2 = st.columns(2)

    with col_chart_1:
        with st.container(border=True):
            st.markdown("#### 🛏️ Bed Occupancy vs. Capacity")
            st.caption("Visual distribution of occupied versus available residential capacity")

            occ_pct = round((occupied_beds / total_capacity * 100), 1) if total_capacity > 0 else 0
            fig_occ = go.Figure(data=[go.Pie(
                labels=["Occupied Beds", "Available Beds"],
                values=[occupied_beds, available_beds],
                hole=0.68,
                marker=dict(colors=["#38BDF8", "#10B981"], line=dict(color="#0F172A", width=3)),
                textinfo="percent",
                hoverinfo="label+value+percent"
            )])
            fig_occ.update_layout(
                **get_plotly_dark_theme(),
                height=260,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                annotations=[dict(text=f"<b>{occ_pct}%</b><br><span style='font-size:11px;'>Occupancy</span>", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="#FFFFFF")]
            )
            st.plotly_chart(fig_occ, use_container_width=True, config={"displayModeBar": False})

    with col_chart_2:
        with st.container(border=True):
            st.markdown("#### 🎓 Resident Demographic by Course")
            st.caption("Distribution of enrolled hostel residents across academic programs")

            courses_labels = list(student_courses.keys())
            courses_counts = list(student_courses.values())

            fig_course = go.Figure(data=[go.Bar(
                x=courses_labels,
                y=courses_counts,
                marker=dict(
                    color=courses_counts,
                    colorscale="Tealgrn",
                    line=dict(color="#00F5D4", width=1.5)
                ),
                text=courses_counts,
                textposition="auto"
            )])
            fig_course.update_layout(
                **get_plotly_dark_theme(),
                height=260,
                xaxis_title=None,
                yaxis_title="Students",
                showlegend=False
            )
            st.plotly_chart(fig_course, use_container_width=True, config={"displayModeBar": False})

    # =========================================================
    # VIRTUAL TOUR SHOWCASE CALLOUT
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        v_col1, v_col2 = st.columns([3, 1])
        with v_col1:
            st.markdown("""
            ### 🎥 Virtual Hostel Tour & 360° Facility Highlights
            Take a cinematic video tour of residential campus blocks A & B, double/quad student rooms, study lounges, dining mess, gym, and 24/7 security.
            """)
        with v_col2:
            st.write("")
            st.write("")
            if st.button("▶️ Launch Tour Gallery", use_container_width=True, type="primary"):
                navigate_fn("Hostel Tour Videos")

    # =========================================================
    # QUICK ACCESS MODULES
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚡ Quick Navigation Command")

    quick_items = [
        ("👨‍🎓", "Student Registration", "Register new residents with photos"),
        ("👤", "Student Profile", "View full resident records & photos"),
        ("🎥", "Hostel Tour Videos", "Stream campus facility tour videos"),
        ("🏠", "Room Management", "Configure hostel rooms & capacities"),
        ("🔑", "Room Allocation", "Assign students to rooms & beds"),
        ("📋", "Attendance", "Daily biometric & manual attendance"),
        ("👨‍👩‍👧", "Parent / Visitor", "Log visitor check-ins & check-outs"),
        ("🚪", "Student Gate Pass", "Issue & track digital entry/exit passes"),
        ("📝", "Complaints", "Track maintenance & grievances"),
        ("📢", "Notice Board", "Publish broadcasts & announcements"),
        ("☁️", "AWS Cloud & Storage", "Inspect S3, EC2 & backup database")
    ]

    for start in range(0, len(quick_items), 3):
        columns = st.columns(3)
        for col, item in zip(columns, quick_items[start:start + 3]):
            icon, module_name, desc = item
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {icon} {module_name}")
                    st.caption(desc)
                    if st.button(f"Open {module_name}", key=f"quick_{module_name}", use_container_width=True):
                        navigate_fn(module_name)
