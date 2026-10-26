import streamlit as st
import time as pytime
from datetime import date
from database.database import get_db_session
from models import Notice


def render_notices():
    st.title("📢 Institutional Notice Board")
    st.caption("Broadcast official announcements, fee schedules, maintenance advisories, and campus holiday notices.")

    with st.form("publish_notice_form"):
        st.subheader("Publish Announcement")
        notice_title = st.text_input("Notice Headline *", placeholder="e.g. Scheduled Water Maintenance in Block A")

        c1, c2 = st.columns(2)
        with c1:
            notice_type = st.selectbox(
                "Category *",
                ["Important", "General", "Maintenance", "Fee Notice", "Holiday", "Campus Event"]
            )
        with c2:
            notice_date = st.date_input("Broadcast Date", value=date.today())

        notice_description = st.text_area("Announcement Details *", placeholder="Full notice body text...")

        publish = st.form_submit_button("Broadcast Notice", type="primary")

    if publish:
        if not notice_title.strip() or not notice_description.strip():
            st.error("Please provide both a notice headline and detailed description.")
        else:
            try:
                with get_db_session() as db:
                    new_n = Notice(
                        title=notice_title.strip(),
                        description=notice_description.strip(),
                        notice_date=str(notice_date),
                        notice_type=notice_type
                    )
                    db.add(new_n)
                st.success("✅ Notice successfully broadcasted!")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Error publishing notice: {e}")

    # =========================================================
    # PUBLISHED NOTICES FEED
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Active Notice Feed")

    with get_db_session() as db:
        notices = db.query(Notice).order_by(Notice.id.desc()).all()

    if notices:
        for n in notices:
            badge_class = "pill-warning" if n.notice_type == "Important" else "pill-info"
            with st.container(border=True):
                c_top, c_del = st.columns([5, 1])
                with c_top:
                    st.markdown(f"""
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
                        <span class="pill-badge {badge_class}">📢 {n.notice_type}</span>
                        <span style="font-size: 12px; color: #94A3B8;">📅 {n.notice_date}</span>
                    </div>
                    <h3 style="margin: 0 0 10px 0; color: #FFFFFF !important; font-size: 20px;">{n.title}</h3>
                    """, unsafe_allow_html=True)
                    st.write(n.description)

                with c_del:
                    if st.button("🗑️ Delete", key=f"del_notice_{n.id}"):
                        try:
                            with get_db_session() as db:
                                t = db.query(Notice).filter(Notice.id == n.id).first()
                                if t:
                                    db.delete(t)
                            st.success("Notice deleted!")
                            pytime.sleep(0.4)
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Failed: {ex}")
    else:
        st.info("No active notices currently published.")
