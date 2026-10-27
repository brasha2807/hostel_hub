import streamlit as st
import time as pytime
from datetime import date
from database.database import get_db_session
from models import Attendance, Student


def render_attendance():
    st.title("📋 Student Attendance Management")
    st.caption("Record and monitor daily resident attendance, track absences, and audit residence status.")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.name.asc()).all()
        student_choices = {
            f"{s.name} ({s.course} · Room {s.room_number or 'N/A'})": s.id
            for s in students
        }

    if not student_choices:
        st.info("Please register students first.")
        return

    col_form, col_quick = st.columns([2, 1])

    with col_form:
        with st.form("attendance_logging_form"):
            st.subheader("Record Attendance")
            sel_student = st.selectbox("Select Resident Student", list(student_choices.keys()))
            c_d, c_s = st.columns(2)
            with c_d:
                att_date = st.date_input("Attendance Date", value=date.today())
            with c_s:
                att_status = st.selectbox("Status", ["Present", "Absent", "On Leave", "Late"])

            submit_att = st.form_submit_button("Save Attendance Record", type="primary")

        if submit_att:
            s_id = student_choices[sel_student]
            try:
                with get_db_session() as db:
                    existing = db.query(Attendance).filter(
                        Attendance.student_id == s_id,
                        Attendance.date == str(att_date)
                    ).first()
                    if existing:
                        existing.status = att_status
                    else:
                        db.add(Attendance(
                            student_id=s_id,
                            date=str(att_date),
                            status=att_status
                        ))
                st.success(f"✅ Attendance recorded: {att_status} on {att_date}")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Error saving attendance: {e}")

    with col_quick:
        with st.container(border=True):
            st.markdown("#### ⚡ Today's Telemetry")
            today_str = str(date.today())
            with get_db_session() as db:
                today_records = db.query(Attendance).filter(Attendance.date == today_str).all()
                present_cnt = sum(1 for a in today_records if a.status == "Present")
                absent_cnt = sum(1 for a in today_records if a.status == "Absent")
                leave_cnt = sum(1 for a in today_records if a.status == "On Leave")

            st.metric("Present Today", present_cnt)
            st.metric("Absent Today", absent_cnt)
            st.metric("On Leave Today", leave_cnt)

    # =========================================================
    # ATTENDANCE AUDIT LOGS
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Attendance History & Logs")

    filter_date = st.date_input("Filter Records by Date", value=date.today(), key="att_filter_date_key")

    with get_db_session() as db:
        query = db.query(Attendance, Student).join(Student, Attendance.student_id == Student.id)
        if filter_date:
            query = query.filter(Attendance.date == str(filter_date))
        records = query.order_by(Attendance.id.desc()).all()

        log_rows = [
            {
                "Log ID": r[0].id,
                "Student": r[1].name,
                "Course": r[1].course,
                "Room": r[1].room_number or "-",
                "Date": r[0].date,
                "Status": r[0].status
            }
            for r in records
        ]

    if log_rows:
        st.dataframe(log_rows, use_container_width=True, hide_index=True)
    else:
        st.info(f"No attendance logs found for {filter_date}.")
