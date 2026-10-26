import streamlit as st
import os

from config.settings import APP_TITLE, APP_SUBTITLE, APP_VERSION, MODULES
from database.database import init_db
from utils.ui_components import inject_custom_css
from utils import photo_utils, aws_utils

# Import Modular Views
from views.dashboard import render_dashboard
from views.tour_videos import render_tour_videos
from views.students import render_student_registration, render_student_profile
from views.rooms import render_room_management, render_room_allocation
from views.attendance import render_attendance
from views.visitors import render_visitors
from views.gate_pass import render_gate_pass
from views.complaints import render_complaints
from views.notices import render_notices
from views.aws_monitor import render_aws_monitor

# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

st.set_page_config(
    page_title=f"{APP_TITLE} | {APP_SUBTITLE}",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema & migrations
init_db()


# =========================================================
# NAVIGATION CONTROLLER
# =========================================================

def navigate_to(module_name):
    """Callback to switch between modules from anywhere in the app."""
    st.session_state["pending_navigation"] = module_name


if "pending_navigation" in st.session_state:
    st.session_state["module_nav_key"] = st.session_state.pop("pending_navigation")


# =========================================================
# SIDEBAR NAVIGATION & BRANDING
# =========================================================

st.sidebar.markdown(f"""
<div style="padding: 10px 0 16px 0;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 6px;">
        <span style="font-size: 34px;">🏨</span>
        <div>
            <div style="
                font-family: 'Outfit', sans-serif;
                font-size: 24px;
                font-weight: 850;
                letter-spacing: 0.5px;
                color: #FFFFFF;
                line-height: 1.1;
            ">
                {APP_TITLE.upper()}
            </div>
            <div style="
                font-size: 11px;
                color: #38BDF8;
                font-weight: 700;
                letter-spacing: 1px;
                text-transform: uppercase;
            ">
                Luxe Campus Edition
            </div>
        </div>
    </div>
    <div style="font-size: 11px; color: #94A3B8; line-height: 1.4;">
        {APP_SUBTITLE}
    </div>
</div>
""", unsafe_allow_html=True)

# LIVE AWS CLOUD STATUS CHIP IN SIDEBAR
aws_info = aws_utils.check_aws_connection()
if aws_info["connected"]:
    st.sidebar.markdown(f"""
    <div style="
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span class="radar-dot"></span>
        <div>
            <div style="font-size: 11px; font-weight: 800; color: #34D399; text-transform: uppercase; letter-spacing: 0.5px;">
                AWS Connected
            </div>
            <div style="font-size: 10px; color: #CBD5E1; font-family: monospace;">
                {aws_info['region']} · #{str(aws_info['account_id'])[-4:]}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style="
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span style="font-size: 14px;">⚡</span>
        <div style="font-size: 11px; font-weight: 700; color: #FBBF24;">
            Local Standalone Mode
        </div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.caption("Workspace Navigation")

selected_module = st.sidebar.selectbox(
    "Select Module",
    MODULES,
    key="module_nav_key"
)

# =========================================================
# THEME & BACKGROUND CLARITY CONTROL
# =========================================================

st.sidebar.divider()
st.sidebar.markdown("""
<div style="font-size: 11px; font-weight: 800; letter-spacing: 1px; color: #38BDF8; text-transform: uppercase; margin-bottom: 6px;">
    🎨 Background Atmosphere
</div>
""", unsafe_allow_html=True)

bg_clarity = st.sidebar.select_slider(
    "Photo Clarity",
    options=["Crystal Clear", "Vivid (Recommended)", "Soft Tint", "Muted"],
    value="Vivid (Recommended)",
    label_visibility="collapsed",
    help="Adjust background photograph prominence and frosted glass opacity across the interface."
)

st.sidebar.divider()
st.sidebar.caption(f"Hostel Hub {APP_VERSION}")
st.sidebar.caption("Administrator: Arpita Behera")

# Inject Awwwards-Level Design System CSS
app_bg_image = photo_utils.get_app_background_uri()
inject_custom_css(bg_clarity=bg_clarity, bg_image_uri=app_bg_image)


# =========================================================
# MODULE ROUTER
# =========================================================

if selected_module == "Dashboard":
    render_dashboard(navigate_to)

elif selected_module == "Hostel Tour Videos":
    render_tour_videos()

elif selected_module == "Student Registration":
    render_student_registration()

elif selected_module == "Student Profile":
    render_student_profile()

elif selected_module == "Room Management":
    render_room_management()

elif selected_module == "Room Allocation":
    render_room_allocation()

elif selected_module == "Attendance":
    render_attendance()

elif selected_module == "Parent / Visitor":
    render_visitors()

elif selected_module == "Student Gate Pass":
    render_gate_pass()

elif selected_module == "Complaints":
    render_complaints()

elif selected_module == "Notice Board":
    render_notices()

elif selected_module == "AWS Cloud & Storage":
    render_aws_monitor()
