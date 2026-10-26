import streamlit as st
import os
import time as pytime
from datetime import date
from database.database import get_db_session
from models import Student, Attendance, Visitor, GatePass, Complaint, Room
from utils import photo_utils


def delete_student_record(student_id):
    """Safely delete a student and all related child records from the database."""
    try:
        with get_db_session() as db:
            # Delete child records first
            db.query(Attendance).filter(Attendance.student_id == student_id).delete()
            db.query(Visitor).filter(Visitor.student_id == student_id).delete()
            db.query(GatePass).filter(GatePass.student_id == student_id).delete()
            db.query(Complaint).filter(Complaint.student_id == student_id).delete()

            stu = db.query(Student).filter(Student.id == student_id).first()
            if stu:
                s_name = stu.name
                # If student had room allocation, decrement room occupied count
                if stu.room_number:
                    room = db.query(Room).filter(Room.room_number == stu.room_number).first()
                    if room and room.occupied > 0:
                        room.occupied -= 1

                # If student had custom uploaded photo, remove local file
                if stu.photo and "static/uploads/students" in stu.photo:
                    full_photo = os.path.join(photo_utils.BASE_DIR, stu.photo)
                    if os.path.exists(full_photo):
                        try:
                            os.remove(full_photo)
                        except Exception:
                            pass
                db.delete(stu)
                return True, s_name
            return False, "Student record not found."
    except Exception as e:
        return False, str(e)


# =========================================================
# MODULE 1: STUDENT REGISTRATION
# =========================================================

def render_student_registration():
    st.title("👨‍🎓 Resident Student Registration")
    st.caption("Enroll new resident students, assign contact details, upload identification portraits, and maintain institutional records.")

    with st.form("student_registration_form"):
        st.subheader("New Student Enrollment Form")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", placeholder="e.g. Aarav Sharma")
            email = st.text_input("Institutional Email *", placeholder="e.g. aarav.sharma@example.edu")
            phone = st.text_input("Mobile Number *", placeholder="e.g. +91 98765 43210")
            course = st.text_input("Degree / Course *", placeholder="e.g. B.Tech Computer Science")
            year = st.selectbox("Academic Year *", [1, 2, 3, 4, 5], index=0)

        with c2:
            parent_name = st.text_input("Parent / Guardian Name", placeholder="e.g. Ramesh Sharma")
            parent_phone = st.text_input("Parent Contact Number", placeholder="e.g. +91 98111 22233")
            address = st.text_area("Permanent Residential Address", placeholder="Street, City, State, PIN...")
            admission_date = st.date_input("Date of Admission", value=date.today())
            profile_status = st.selectbox("Enrollment Status", ["Active", "Inactive", "On Leave"])

        st.markdown("##### Profile Photo Upload")
        photo_upload = st.file_uploader(
            "Upload Portrait Photo (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="reg_photo_upload_input"
        )

        submit = st.form_submit_button("Enroll Resident Student", type="primary")

    if submit:
        if not all([name.strip(), email.strip(), phone.strip(), course.strip()]):
            st.error("Please fill in all mandatory fields (Name, Email, Phone, Course).")
        else:
            try:
                with get_db_session() as db:
                    existing = db.query(Student).filter(Student.email == email.strip()).first()
                    if existing:
                        st.error("A student with this email is already registered.")
                    else:
                        saved_photo = None
                        if photo_upload:
                            saved_photo = photo_utils.save_uploaded_photo(photo_upload)

                        new_student = Student(
                            name=name.strip(),
                            email=email.strip(),
                            phone=phone.strip(),
                            course=course.strip(),
                            year=int(year),
                            parent_name=parent_name.strip(),
                            parent_phone=parent_phone.strip(),
                            address=address.strip(),
                            admission_date=str(admission_date),
                            profile_status=profile_status,
                            photo=saved_photo
                        )
                        db.add(new_student)
                st.success("✅ Student registered successfully with profile portrait!")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Registration failed: {e}")

    # =========================================================
    # REGISTERED RESIDENTS DIRECTORY TABLE
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Registered Residents Directory")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.id.desc()).all()
        student_rows = [
            {
                "Photo": photo_utils.get_student_photo_uri(s),
                "ID": f"#{s.id:04d}",
                "Name": s.name,
                "Email": s.email,
                "Phone": s.phone,
                "Course": s.course,
                "Year": f"Year {s.year}",
                "Room": s.room_number or "Unassigned",
                "Status": getattr(s, "profile_status", "Active")
            }
            for s in students
        ]

    if student_rows:
        st.dataframe(
            student_rows,
            column_config={
                "Photo": st.column_config.ImageColumn(
                    "Photo",
                    help="Resident Portrait",
                    width="small"
                )
            },
            use_container_width=True,
            hide_index=True
        )

        # Removal / Delete section
        with st.expander("🗑️ Delete / Unregister a Student", expanded=False):
            st.caption("Permanently delete a resident record from the system. Requires confirmation.")
            del_choices = {f"#{s.id:04d} - {s.name} ({s.course})": s.id for s in students}
            sel_label = st.selectbox("Select Student to Remove", list(del_choices.keys()), key="del_stu_select")
            del_id = del_choices[sel_label]

            target_stu = next((s for s in students if s.id == del_id), None)
            if target_stu:
                st.warning(f"⚠️ You are about to permanently remove **{target_stu.name}** (#{target_stu.id:04d}).")
                confirm = st.checkbox(f"Confirm permanent deletion of {target_stu.name}", key="confirm_del_reg_chk")
                if st.button("🚨 Permanently Remove Student", type="primary", disabled=not confirm, key="btn_del_stu_reg"):
                    ok, msg = delete_student_record(del_id)
                    if ok:
                        st.success(f"Student {msg} deleted successfully!")
                        pytime.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"Deletion failed: {msg}")
    else:
        st.info("No resident students registered yet.")


# =========================================================
# MODULE 2: STUDENT PROFILE
# =========================================================

def render_student_profile():
    st.title("👤 Resident Student Profile & Dossier")
    st.caption("Detailed institutional profile, room allocation status, high-resolution portrait, and activity telemetry.")

    with get_db_session() as db:
        students = db.query(Student).all()

    if not students:
        st.info("No students found. Please enroll a resident student first.")
        return

    profile_mode = st.radio(
        "Select Dossier View",
        ["👤 Individual Resident Profile", "👥 Student Photo Directory (All Residents)"],
        horizontal=True,
        key="student_profile_mode_toggle"
    )

    # ---------------------------------------------------------
    # VIEW 1: INDIVIDUAL STUDENT PROFILE
    # ---------------------------------------------------------
    if profile_mode == "👤 Individual Resident Profile":
        student_dict = {
            f"#{s.id:04d} · {s.name} ({s.course} · Yr {s.year})": s.id
            for s in students
        }

        default_idx = 0
        preset_id = st.session_state.get("profile_selected_student_id")
        if preset_id:
            for idx, sid in enumerate(student_dict.values()):
                if sid == preset_id:
                    default_idx = idx
                    break

        selected_label = st.selectbox(
            "Select Resident Student",
            list(student_dict.keys()),
            index=default_idx,
            key="individual_student_selector"
        )
        selected_id = student_dict[selected_label]
        st.session_state["profile_selected_student_id"] = selected_id

        with get_db_session() as db:
            student = db.query(Student).filter(Student.id == selected_id).first()
            attendance_logs = db.query(Attendance).filter(Attendance.student_id == selected_id).order_by(Attendance.date.desc()).limit(8).all()
            gate_passes = db.query(GatePass).filter(GatePass.student_id == selected_id).order_by(GatePass.pass_date.desc()).limit(8).all()
            complaints = db.query(Complaint).filter(Complaint.student_id == selected_id).order_by(Complaint.complaint_date.desc()).limit(8).all()

        if student:
            stu_banner = photo_utils.get_student_banner_uri()
            stu_photo = photo_utils.get_student_photo_uri(student)
            status_str = getattr(student, "profile_status", "Active") or "Active"
            badge_class = "pill-success" if status_str == "Active" else "pill-neutral"
            room_disp = student.room_number if student.room_number else "Not Allocated"

            # 1. PROFILE COVER BANNER
            st.markdown(f"""
            <div style="
                width: 100%;
                height: 240px;
                border-radius: 24px 24px 0 0;
                position: relative;
                background: linear-gradient(180deg, rgba(8, 13, 26, 0.3) 0%, rgba(8, 13, 26, 0.85) 100%),
                            url('{stu_banner}');
                background-size: cover;
                background-position: center;
                border: 1px solid rgba(255, 255, 255, 0.16);
                border-bottom: none;
            ">
                <div style="position: absolute; top: 16px; right: 20px; display: flex; gap: 8px;">
                    <span class="pill-badge {badge_class}">● {status_str}</span>
                    <span class="pill-badge pill-info">ID: #{student.id:04d}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # 2. CENTERED HIGH-RES PROFILE CARD
            st.markdown(f"""
            <div style="
                background: rgba(15, 23, 42, 0.90);
                backdrop-filter: blur(20px);
                border-radius: 0 0 24px 24px;
                padding: 0 32px 30px 32px;
                margin-bottom: 24px;
                border: 1px solid rgba(255, 255, 255, 0.14);
                border-top: none;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
            ">
                <div style="position: relative; margin-top: -95px; margin-bottom: 12px;">
                    <img src="{stu_photo}" style="
                        width: 190px;
                        height: 190px;
                        border-radius: 50%;
                        border: 6px solid #0F172A;
                        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.3);
                        object-fit: cover;
                        background: #0B132B;
                    " alt="{student.name}">
                </div>
                <div>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #38BDF8; font-weight: 800;">
                        Hostel Resident Profile
                    </div>
                    <h1 style="margin: 6px 0 10px 0; font-size: 36px; color: #FFFFFF !important; font-weight: 850;">
                        {student.name}
                    </h1>
                    <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px;">
                        <span class="pill-badge pill-info">🎓 {student.course}</span>
                        <span class="pill-badge pill-info">📚 Year {student.year}</span>
                        <span class="pill-badge pill-warning">🏠 Room {room_disp}</span>
                        <span class="pill-badge pill-neutral">📧 {student.email}</span>
                        <span class="pill-badge pill-neutral">📞 {student.phone}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # FULL RESOLUTION PHOTO PREVIEW TOOL
            with st.expander("🔍 View Full-Resolution Uncropped Portrait", expanded=False):
                c_img, c_meta = st.columns([1, 1])
                with c_img:
                    st.image(stu_photo, caption=f"Portrait: {student.name}", use_container_width=True)
                with c_meta:
                    st.markdown(f"""
                    ##### Portrait Metadata
                    - **Resident:** {student.name}
                    - **Student ID:** #{student.id:04d}
                    - **Room Number:** {room_disp}
                    - **Course:** {student.course} · Year {student.year}
                    - **Storage Engine:** Local Static / AWS S3 Synced
                    """)

            # PHOTO MANAGEMENT EXPANDER
            with st.expander("📷 Change / Update Resident Photo", expanded=False):
                tab_file, tab_webcam, tab_avatars = st.tabs([
                    "📁 Upload Image File",
                    "📸 Live Webcam Capture",
                    "🎨 Preset Avatar Library"
                ])

                new_photo_path = None

                with tab_file:
                    up_img = st.file_uploader(
                        "Upload photo file (JPG, PNG, WEBP)",
                        type=["jpg", "jpeg", "png", "webp"],
                        key=f"edit_photo_file_{student.id}"
                    )
                    if up_img:
                        st.image(up_img, caption="Preview Upload", width=140)
                        if st.button("Save Uploaded Photo", key=f"btn_save_up_{student.id}", type="primary"):
                            new_photo_path = photo_utils.save_uploaded_photo(up_img, student.id)

                with tab_webcam:
                    cam_img = st.camera_input("Take a portrait using your webcam", key=f"edit_cam_{student.id}")
                    if cam_img:
                        if st.button("Save Webcam Snapshot", key=f"btn_save_cam_{student.id}", type="primary"):
                            new_photo_path = photo_utils.save_uploaded_photo(cam_img, student.id)

                with tab_avatars:
                    st.caption("Select a curated avatar preset:")
                    cols_av = st.columns(6)
                    for av_i in range(1, 18):
                        col = cols_av[(av_i - 1) % 6]
                        rel_av_path = f"static/avatars/avatar_{av_i}.jpg"
                        av_uri = photo_utils.get_image_data_uri(rel_av_path)
                        with col:
                            st.markdown(
                                f'<img src="{av_uri}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; border: 2px solid #38BDF8; display: block; margin: 0 auto 6px auto;">',
                                unsafe_allow_html=True
                            )
                            if st.button(f"#{av_i}", key=f"btn_av_{student.id}_{av_i}", use_container_width=True):
                                new_photo_path = rel_av_path

                if new_photo_path:
                    try:
                        with get_db_session() as db:
                            target = db.query(Student).filter(Student.id == student.id).first()
                            if target:
                                target.photo = new_photo_path
                        st.success("✅ Student portrait updated successfully!")
                        pytime.sleep(0.4)
                        st.rerun()
                    except Exception as pe:
                        st.error(f"Failed to update photo: {pe}")

            # PROFILE DETAILS TABS
            tab1, tab2, tab3, tab4 = st.tabs([
                "📋 Academic & Personal Details",
                "👨‍👩‍👧 Guardian & Residence",
                "🏨 Room & Facilities",
                "📊 Attendance & Passes Activity"
            ])

            with tab1:
                t1_c1, t1_c2 = st.columns(2)
                with t1_c1:
                    with st.container(border=True):
                        st.markdown("**Student ID:** " + f"#{student.id:04d}")
                        st.markdown("**Full Name:** " + student.name)
                        st.markdown("**Email:** " + student.email)
                        st.markdown("**Phone:** " + student.phone)
                with t1_c2:
                    with st.container(border=True):
                        st.markdown("**Course / Program:** " + student.course)
                        st.markdown("**Academic Year:** " + f"Year {student.year}")
                        st.markdown("**Admission Date:** " + (student.admission_date or "Not recorded"))
                        st.markdown("**Status:** " + status_str)

            with tab2:
                t2_c1, t2_c2 = st.columns(2)
                with t2_c1:
                    with st.container(border=True):
                        st.markdown("**Parent / Guardian:** " + (student.parent_name or "Not provided"))
                        st.markdown("**Parent Phone:** " + (student.parent_phone or "Not provided"))
                with t2_c2:
                    with st.container(border=True):
                        st.markdown("**Permanent Address:**")
                        st.write(student.address or "Not recorded")

            with tab3:
                st.markdown("#### Residential Assignment")
                with st.container(border=True):
                    r_c1, r_c2 = st.columns(2)
                    with r_c1:
                        st.markdown(f"**Allocated Room:** {room_disp}")
                        st.markdown("**Residential Complex:** Main Campus Hall · Block A / B")
                    with r_c2:
                        st.markdown("**Included Amenities:** High-speed Wi-Fi, 4-Meal Mess, Gym, Study Lounge")
                        st.caption("To reallocate or checkout, visit the Room Allocation module.")

            with tab4:
                st.markdown("#### Activity Telemetry")
                act_c1, act_c2 = st.columns(2)
                with act_c1:
                    st.markdown("##### Recent Attendance")
                    if attendance_logs:
                        st.dataframe(
                            [{"Date": a.date, "Status": a.status} for a in attendance_logs],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.caption("No attendance logs recorded.")

                with act_c2:
                    st.markdown("##### Recent Gate Passes")
                    if gate_passes:
                        st.dataframe(
                            [{"Date": g.pass_date, "Reason": g.reason, "Status": g.status} for g in gate_passes],
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.caption("No gate pass records.")

            # PERMANENT REMOVAL SECTION
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🗑️ Permanent Deletion (Danger Zone)", expanded=False):
                st.error(f"⚠️ You are about to permanently delete **{student.name}** (#{student.id:04d}).")
                conf_del = st.checkbox(f"Confirm deletion of {student.name}", key=f"prof_del_chk_{student.id}")
                if st.button("🚨 Permanently Remove Student Record", type="primary", disabled=not conf_del, key=f"prof_btn_del_{student.id}"):
                    ok, msg = delete_student_record(student.id)
                    if ok:
                        st.success(f"Student {msg} deleted successfully!")
                        st.session_state.pop("profile_selected_student_id", None)
                        pytime.sleep(0.4)
                        st.rerun()
                    else:
                        st.error(f"Failed: {msg}")

    # ---------------------------------------------------------
    # VIEW 2: PHOTO DIRECTORY GALLERY
    # ---------------------------------------------------------
    else:
        st.subheader("👥 Resident Students Photo Gallery")
        st.caption("Visual roster of enrolled students with high-resolution portraits.")

        search = st.text_input("🔍 Search Residents by Name or Course", placeholder="e.g. Aarav, CSE, IT, BCA...")
        filtered = students
        if search.strip():
            kw = search.strip().lower()
            filtered = [s for s in students if kw in s.name.lower() or kw in s.course.lower() or kw in s.email.lower()]

        st.markdown(f"**Showing {len(filtered)} of {len(students)} resident profiles**")

        for row_i in range(0, len(filtered), 3):
            cols = st.columns(3)
            for offset, s in enumerate(filtered[row_i:row_i + 3]):
                with cols[offset]:
                    s_photo = photo_utils.get_student_photo_uri(s)
                    s_stat = getattr(s, "profile_status", "Active") or "Active"
                    s_badge = "pill-success" if s_stat == "Active" else "pill-neutral"
                    r_num = s.room_number or "Unassigned"

                    with st.container(border=True):
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px 0;">
                            <img src="{s_photo}" style="
                                width: 96px;
                                height: 96px;
                                border-radius: 50%;
                                object-fit: cover;
                                border: 3px solid #38BDF8;
                                box-shadow: 0 8px 20px rgba(0,0,0,0.4);
                                margin-bottom: 10px;
                            " alt="{s.name}">
                            <div style="font-size: 18px; font-weight: 800; color: #FFFFFF; font-family: 'Outfit', sans-serif;">
                                {s.name}
                            </div>
                            <div style="font-size: 13px; color: #94A3B8; margin: 4px 0 8px 0;">
                                {s.course} · Year {s.year}
                            </div>
                            <div style="display: flex; justify-content: center; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;">
                                <span class="pill-badge {s_badge}">● {s_stat}</span>
                                <span class="pill-badge pill-info">🏠 {r_num}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button("Inspect Profile", key=f"btn_gallery_view_{s.id}", use_container_width=True):
                            st.session_state["profile_selected_student_id"] = s.id
                            st.session_state["student_profile_mode_toggle"] = "👤 Individual Resident Profile"
                            st.rerun()
