import streamlit as st
import time as pytime
from datetime import date, time, datetime
from database.database import get_db_session
from models import GatePass, Student


def render_gate_pass():
    st.title("🚪 Student Gate Pass Management")
    st.caption("Issue digital movement gate passes, track campus departure/re-entry, and maintain perimeter security.")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.name.asc()).all()

    if not students:
        st.info("Please register students first.")
        return

    student_choices = {
        f"{s.name} ({s.course} · Room {s.room_number or 'N/A'})": s.id
        for s in students
    }

    with st.form("gate_pass_issue_form"):
        st.subheader("Issue New Movement Pass")
        sel_student = st.selectbox("Resident Student *", list(student_choices.keys()))
        reason = st.text_input("Reason for Leaving Campus *", placeholder="e.g. Weekend Home Visit / Library / Medical Appointment")

        c1, c2, c3 = st.columns(3)
        with c1:
            pass_date = st.date_input("Departure Date", value=date.today())
        with c2:
            out_time = st.time_input("Out Time", value=time(10, 0))
        with c3:
            already_returned = st.checkbox("Student already returned")

        in_time = None
        if already_returned:
            in_time = st.time_input("In Time", value=time(18, 0))

        submit_pass = st.form_submit_button("Issue Gate Pass", type="primary")

    if submit_pass:
        if not reason.strip():
            st.error("Please provide a departure reason.")
        else:
            try:
                with get_db_session() as db:
                    new_gp = GatePass(
                        student_id=student_choices[sel_student],
                        reason=reason.strip(),
                        pass_date=str(pass_date),
                        out_time=str(out_time),
                        in_time=str(in_time) if in_time else None,
                        status="Returned" if already_returned else "Out"
                    )
                    db.add(new_gp)
                st.success("✅ Digital Gate Pass successfully issued!")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Error issuing gate pass: {e}")

    # =========================================================
    # ACTIVE & PAST PASSES
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Movement Pass Register")

    pass_filter = st.radio("Filter Passes", ["All Passes", "Currently Out (Active)", "Returned"], horizontal=True)

    with get_db_session() as db:
        query = db.query(GatePass, Student).join(Student, GatePass.student_id == Student.id)
        if pass_filter == "Currently Out (Active)":
            query = query.filter(GatePass.status == "Out")
        elif pass_filter == "Returned":
            query = query.filter(GatePass.status == "Returned")

        passes = query.order_by(GatePass.id.desc()).all()

        pass_rows = [
            {
                "Pass ID": f"GP-{p[0].id:04d}",
                "Student": p[1].name,
                "Room": p[1].room_number or "-",
                "Reason": p[0].reason,
                "Date": p[0].pass_date,
                "Departure": p[0].out_time,
                "Arrival": p[0].in_time or "Pending Return",
                "Status": p[0].status
            }
            for p in passes
        ]

    if pass_rows:
        st.dataframe(pass_rows, use_container_width=True, hide_index=True)

        # Quick Return Action for Active Passes
        active_passes = [p for p in passes if p[0].status == "Out"]
        if active_passes:
            with st.expander("⚡ Quick Check-in (Mark Student as Returned)", expanded=False):
                act_choices = {f"GP-{p[0].id:04d} · {p[1].name} ({p[0].reason})": p[0].id for p in active_passes}
                sel_active_pass = st.selectbox("Select Active Movement Pass", list(act_choices.keys()))
                pass_target_id = act_choices[sel_active_pass]

                if st.button("Mark as Returned Now", type="primary", key="btn_mark_returned"):
                    try:
                        with get_db_session() as db:
                            target = db.query(GatePass).filter(GatePass.id == pass_target_id).first()
                            if target:
                                target.status = "Returned"
                                target.in_time = datetime.now().strftime("%H:%M:%S")
                        st.success("✅ Student re-entry recorded successfully!")
                        pytime.sleep(0.4)
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error updating pass: {err}")
    else:
        st.info("No gate passes found for the selected filter.")
