import streamlit as st
import time as pytime
from datetime import date, time
from database.database import get_db_session
from models import Visitor, Student


def render_visitors():
    st.title("👨‍👩‍👧 Parent & Visitor Log Management")
    st.caption("Register campus visitors, monitor entry & exit times, and record institutional security compliance.")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.name.asc()).all()
        student_choices = {
            f"{s.name} ({s.course} · Room {s.room_number or 'N/A'})": s.id
            for s in students
        }

    if not student_choices:
        st.info("Please register students first.")
        return

    with st.form("visitor_checkin_form"):
        st.subheader("Log Visitor Entry")
        sel_student = st.selectbox("Resident Student Visited *", list(student_choices.keys()))

        c1, c2, c3 = st.columns(3)
        with c1:
            visitor_name = st.text_input("Visitor Full Name *", placeholder="e.g. Sunita Behera")
        with c2:
            relation = st.text_input("Relationship to Resident *", placeholder="e.g. Mother / Uncle / Guardian")
        with c3:
            visitor_phone = st.text_input("Visitor Phone Number *", placeholder="e.g. +91 98765 00000")

        c4, c5, c6 = st.columns(3)
        with c4:
            visit_date = st.date_input("Visit Date", value=date.today())
        with c5:
            in_time = st.time_input("Entry Time (In)", value=time(10, 0))
        with c6:
            out_time = st.time_input("Expected / Actual Exit Time (Out)", value=time(12, 0))

        purpose = st.text_input("Purpose of Campus Visit", placeholder="e.g. Semester Fee Payment & Personal Visit")

        submit_vis = st.form_submit_button("Record Visitor Entry", type="primary")

    if submit_vis:
        if not all([visitor_name.strip(), relation.strip(), visitor_phone.strip()]):
            st.error("Please fill in visitor name, relationship, and contact number.")
        else:
            try:
                with get_db_session() as db:
                    new_vis = Visitor(
                        student_id=student_choices[sel_student],
                        visitor_name=visitor_name.strip(),
                        relation=relation.strip(),
                        phone=visitor_phone.strip(),
                        visit_date=str(visit_date),
                        in_time=str(in_time),
                        out_time=str(out_time),
                        purpose=purpose.strip()
                    )
                    db.add(new_vis)
                st.success("✅ Visitor entry successfully recorded in security register!")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Error logging visitor: {e}")

    # =========================================================
    # RECENT VISITOR RECORDS TABLE
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Security Visitor Register")

    with get_db_session() as db:
        records = db.query(Visitor, Student).join(Student, Visitor.student_id == Student.id).order_by(Visitor.id.desc()).all()

        vis_rows = [
            {
                "Pass #": f"V-{r[0].id:04d}",
                "Visitor Name": r[0].visitor_name,
                "Relation": r[0].relation,
                "Contact": r[0].phone,
                "Resident Student": r[1].name,
                "Room": r[1].room_number or "-",
                "Date": r[0].visit_date,
                "In Time": r[0].in_time,
                "Out Time": r[0].out_time or "-",
                "Purpose": r[0].purpose or "Personal"
            }
            for r in records
        ]

    if vis_rows:
        st.dataframe(vis_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No visitor logs registered yet.")
