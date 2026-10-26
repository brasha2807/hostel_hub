import streamlit as st
import time as pytime
from database.database import get_db_session
from models import Room, Student


# =========================================================
# MODULE: ROOM MANAGEMENT
# =========================================================

def render_room_management():
    st.title("🏠 Hostel Room Management")
    st.caption("Configure hostel residential rooms, assign bed capacities, and monitor physical floor readiness.")

    with st.form("room_management_form"):
        st.subheader("Add New Residential Room")
        c1, c2 = st.columns(2)
        with c1:
            room_number = st.text_input("Room Identifier *", placeholder="e.g. A-101 or B-204")
        with c2:
            capacity = st.number_input("Bed Capacity *", min_value=1, max_value=10, value=2, step=1)

        add_room = st.form_submit_button("Create Room Record", type="primary")

    if add_room:
        if not room_number.strip():
            st.error("Please provide a valid room number.")
        else:
            try:
                with get_db_session() as db:
                    existing = db.query(Room).filter(Room.room_number == room_number.strip()).first()
                    if existing:
                        st.error(f"Room '{room_number.strip()}' already exists.")
                    else:
                        db.add(Room(
                            room_number=room_number.strip(),
                            capacity=int(capacity),
                            occupied=0
                        ))
                st.success(f"✅ Room {room_number.strip()} (Capacity: {capacity}) registered successfully!")
                pytime.sleep(0.4)
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create room: {e}")

    # =========================================================
    # ROOM INVENTORY DIRECTORY
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🗄️ Residential Room Inventory")

    with get_db_session() as db:
        rooms = db.query(Room).order_by(Room.room_number.asc()).all()
        # Also fetch occupants for each room
        occupants_map = {}
        for s in db.query(Student).filter(Student.room_number.isnot(None)).all():
            occupants_map.setdefault(s.room_number, []).append(s.name)

        room_data = [
            {
                "ID": r.id,
                "Room Number": r.room_number,
                "Total Capacity": r.capacity,
                "Occupied Beds": r.occupied,
                "Available Beds": max(0, r.capacity - r.occupied),
                "Current Residents": ", ".join(occupants_map.get(r.room_number, [])) or "None"
            }
            for r in rooms
        ]

    if room_data:
        st.dataframe(room_data, use_container_width=True, hide_index=True)
    else:
        st.info("No rooms have been registered yet.")


# =========================================================
# MODULE: ROOM ALLOCATION & OCCUPANCY
# =========================================================

def render_room_allocation():
    st.title("🔑 Room Allocation & Resident Bed Assignment")
    st.caption("Allocate students to available beds, inspect occupants per room, or process student check-out / deallocation.")

    with get_db_session() as db:
        students = db.query(Student).order_by(Student.name.asc()).all()
        rooms = db.query(Room).order_by(Room.room_number.asc()).all()

        unallocated_students = [s for s in students if not s.room_number]
        allocated_students = [s for s in students if s.room_number]
        available_rooms = [r for r in rooms if r.occupied < r.capacity]

    tab_alloc, tab_dealloc = st.tabs(["➕ Allocate Student to Bed", "📤 Check-out / Deallocate Student"])

    with tab_alloc:
        if not students:
            st.warning("Please register students first.")
        elif not unallocated_students:
            st.success("🎉 All registered students are currently allocated to rooms!")
        elif not available_rooms:
            st.error("No vacant beds are currently available in any room. Please add more rooms or deallocate residents.")
        else:
            student_choices = {
                f"{s.name} ({s.course} · #{s.id:04d})": s.id
                for s in unallocated_students
            }
            room_choices = {
                f"Room {r.room_number} ({r.occupied}/{r.capacity} occupied · {r.capacity - r.occupied} beds free)": r.id
                for r in available_rooms
            }

            with st.form("allocation_action_form"):
                st.subheader("Assign Resident to Room")
                sel_stu = st.selectbox("Select Student to Allocate", list(student_choices.keys()))
                sel_room = st.selectbox("Select Available Room", list(room_choices.keys()))
                submit_alloc = st.form_submit_button("Confirm Bed Allocation", type="primary")

            if submit_alloc:
                stu_id = student_choices[sel_stu]
                room_id = room_choices[sel_room]
                try:
                    with get_db_session() as db:
                        target_room = db.query(Room).filter(Room.id == room_id).first()
                        target_stu = db.query(Student).filter(Student.id == stu_id).first()

                        if target_room and target_room.occupied < target_room.capacity and target_stu:
                            target_stu.room_number = target_room.room_number
                            target_room.occupied += 1
                            st.success(f"✅ {target_stu.name} has been assigned to Room {target_room.room_number}!")
                            pytime.sleep(0.4)
                            st.rerun()
                        else:
                            st.error("Allocation failed: Room capacity exceeded.")
                except Exception as ex:
                    st.error(f"Error: {ex}")

    with tab_dealloc:
        if not allocated_students:
            st.info("No students are currently allocated to any room.")
        else:
            dealloc_choices = {
                f"{s.name} (Room {s.room_number} · {s.course})": s.id
                for s in allocated_students
            }

            with st.form("deallocation_form"):
                st.subheader("Process Resident Check-out")
                sel_dealloc = st.selectbox("Select Resident to Check-out", list(dealloc_choices.keys()))
                submit_dealloc = st.form_submit_button("Check-out / Free Bed", type="primary")

            if submit_dealloc:
                s_id = dealloc_choices[sel_dealloc]
                try:
                    with get_db_session() as db:
                        target_stu = db.query(Student).filter(Student.id == s_id).first()
                        if target_stu and target_stu.room_number:
                            r_num = target_stu.room_number
                            target_room = db.query(Room).filter(Room.room_number == r_num).first()
                            if target_room and target_room.occupied > 0:
                                target_room.occupied -= 1
                            target_stu.room_number = None
                            st.success(f"✅ {target_stu.name} has checked out of Room {r_num}. Bed freed!")
                            pytime.sleep(0.4)
                            st.rerun()
                except Exception as ex:
                    st.error(f"Deallocation error: {ex}")

    # =========================================================
    # CURRENT OCCUPANCY OVERVIEW
    # =========================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📊 Live Room Occupancy Table")

    with get_db_session() as db:
        all_rooms = db.query(Room).order_by(Room.room_number.asc()).all()
        occupancy_rows = [
            {
                "Room": r.room_number,
                "Capacity": r.capacity,
                "Occupied Beds": r.occupied,
                "Available Beds": max(0, r.capacity - r.occupied),
                "Status": "Full" if r.occupied >= r.capacity else f"{r.capacity - r.occupied} Vacant"
            }
            for r in all_rooms
        ]

    st.dataframe(occupancy_rows, use_container_width=True, hide_index=True)
