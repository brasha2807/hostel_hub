import streamlit as st
import time as pytime
from datetime import date
from database.database import get_db_session
from models import Complaint, Student


def render_complaints():
    st.title("📝 Grievance & Maintenance Management")
    st.caption("Log facility tickets, track resolution status, and streamline residential student maintenance.")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.name.asc()).all()

    if not students:
        st.info("Please register students first.")
        return

    student_choices = {
        f"{s.name} ({s.course} · Room {s.room_number or 'N/A'})": s.id
        for s in students
    }

    tab_log, tab_manage = st.tabs(["➕ Submit New Complaint / Ticket", "⚙️ Manage & Resolve Open Tickets"])

    with tab_log:
        with st.form("complaint_submission_form"):
            st.subheader("Submit Maintenance Request")
            sel_student = st.selectbox("Resident Student *", list(student_choices.keys()))

            c1, c2 = st.columns(2)
            with c1:
                comp_type = st.selectbox(
                    "Grievance Category *",
                    ["Room", "Food / Mess", "Cleanliness", "Maintenance", "Water Supply", "Electricity", "Wi-Fi & Network", "Other"]
                )
            with c2:
                comp_date = st.date_input("Date Reported", value=date.today())

            description = st.text_area("Issue Description *", placeholder="Detailed explanation of the issue (e.g. Washroom tap leaking, fan speed regulator broken, etc.)...")

            submit_comp = st.form_submit_button("Submit Ticket", type="primary")

        if submit_comp:
            if not description.strip():
                st.error("Please provide a description of the issue.")
            else:
                try:
                    with get_db_session() as db:
                        new_comp = Complaint(
                            student_id=student_choices[sel_student],
                            complaint_type=comp_type,
                            description=description.strip(),
                            complaint_date=str(comp_date),
                            status="Pending"
                        )
                        db.add(new_comp)
                    st.success("✅ Maintenance ticket submitted successfully!")
                    pytime.sleep(0.4)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error submitting ticket: {e}")

    with tab_manage:
        st.subheader("Update Ticket Resolution Status")
        with get_db_session() as db:
            open_tickets = db.query(Complaint, Student).join(Student, Complaint.student_id == Student.id).order_by(Complaint.id.desc()).all()

        if open_tickets:
            ticket_options = {
                f"#{c[0].id:04d} · [{c[0].status}] {c[0].complaint_type} - {c[1].name} ({c[0].complaint_date})": c[0].id
                for c in open_tickets
            }
            sel_ticket_label = st.selectbox("Select Ticket to Update", list(ticket_options.keys()))
            sel_ticket_id = ticket_options[sel_ticket_label]

            target_c = next((c[0] for c in open_tickets if c[0].id == sel_ticket_id), None)
            if target_c:
                with st.container(border=True):
                    st.markdown(f"**Ticket Description:** {target_c.description}")
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Resolved", "Closed"], index=["Pending", "In Progress", "Resolved", "Closed"].index(target_c.status) if target_c.status in ["Pending", "In Progress", "Resolved", "Closed"] else 0)
                    with c_s2:
                        st.write("")
                        st.write("")
                        if st.button("Update Status Now", type="primary"):
                            try:
                                with get_db_session() as db:
                                    t = db.query(Complaint).filter(Complaint.id == sel_ticket_id).first()
                                    if t:
                                        t.status = new_status
                                st.success(f"Ticket #{sel_ticket_id:04d} updated to '{new_status}'!")
                                pytime.sleep(0.4)
                                st.rerun()
                            except Exception as ex:
                                st.error(f"Failed to update status: {ex}")
        else:
            st.info("No tickets available to manage.")

    # =========================================================
    # COMPLAINTS REGISTER TABLE
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Institutional Grievance Register")

    with get_db_session() as db:
        complaints_list = db.query(Complaint, Student).join(Student, Complaint.student_id == Student.id).order_by(Complaint.id.desc()).all()

        c_rows = [
            {
                "Ticket #": f"TKT-{c[0].id:04d}",
                "Resident": c[1].name,
                "Room": c[1].room_number or "-",
                "Category": c[0].complaint_type,
                "Description": c[0].description,
                "Date": c[0].complaint_date,
                "Status": c[0].status
            }
            for c in complaints_list
        ]

    if c_rows:
        st.dataframe(c_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No complaints on file.")
