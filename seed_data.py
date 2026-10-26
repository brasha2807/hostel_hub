from datetime import date, timedelta
from database.database import Base, engine, SessionLocal

from models.student import Student
from models.room import Room
from models.attendance import Attendance
from models.visitor import Visitor
from models.gate_pass import GatePass
from models.complaint import Complaint
from models.notice import Notice


# Create all tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()


# -------------------------------------------------
# 1. STUDENT DATA - 50 DEMO RECORDS
# -------------------------------------------------

students_data = [
    ("Aarav Kumar", "aarav.kumar01@example.com", "9000000001", "B.Tech CSE", 1),
    ("Ananya Das", "ananya.das02@example.com", "9000000002", "B.Tech CSE", 2),
    ("Rohan Patel", "rohan.patel03@example.com", "9000000003", "B.Tech ECE", 3),
    ("Priya Singh", "priya.singh04@example.com", "9000000004", "B.Tech CSE", 4),
    ("Aditya Mishra", "aditya.mishra05@example.com", "9000000005", "BCA", 2),
    ("Sneha Sharma", "sneha.sharma06@example.com", "9000000006", "BCA", 1),
    ("Rahul Das", "rahul.das07@example.com", "9000000007", "B.Tech EEE", 3),
    ("Pooja Nayak", "pooja.nayak08@example.com", "9000000008", "B.Tech CSE", 2),
    ("Abhishek Rout", "abhishek.rout09@example.com", "9000000009", "B.Tech ME", 4),
    ("Neha Mohanty", "neha.mohanty10@example.com", "9000000010", "B.Tech CSE", 1),

    ("Sourav Behera", "sourav.behera11@example.com", "9000000011", "B.Tech ECE", 2),
    ("Riya Das", "riya.das12@example.com", "9000000012", "BCA", 3),
    ("Aman Kumar", "aman.kumar13@example.com", "9000000013", "B.Tech CSE", 4),
    ("Simran Kaur", "simran.kaur14@example.com", "9000000014", "B.Tech IT", 2),
    ("Vivek Singh", "vivek.singh15@example.com", "9000000015", "B.Tech CSE", 3),
    ("Kajal Sahu", "kajal.sahu16@example.com", "9000000016", "B.Tech EEE", 1),
    ("Manish Pradhan", "manish.pradhan17@example.com", "9000000017", "B.Tech ME", 2),
    ("Ishita Das", "ishita.das18@example.com", "9000000018", "BCA", 1),
    ("Karan Patel", "karan.patel19@example.com", "9000000019", "B.Tech CSE", 3),
    ("Swati Mishra", "swati.mishra20@example.com", "9000000020", "B.Tech IT", 4),

    ("Deepak Rout", "deepak.rout21@example.com", "9000000021", "B.Tech CSE", 2),
    ("Nikita Behera", "nikita.behera22@example.com", "9000000022", "B.Tech ECE", 1),
    ("Arjun Sharma", "arjun.sharma23@example.com", "9000000023", "B.Tech ME", 3),
    ("Muskan Das", "muskan.das24@example.com", "9000000024", "BCA", 2),
    ("Ritesh Kumar", "ritesh.kumar25@example.com", "9000000025", "B.Tech CSE", 4),
    ("Sakshi Nayak", "sakshi.nayak26@example.com", "9000000026", "B.Tech IT", 1),
    ("Vishal Mohanty", "vishal.mohanty27@example.com", "9000000027", "B.Tech EEE", 3),
    ("Tanisha Singh", "tanisha.singh28@example.com", "9000000028", "B.Tech CSE", 2),
    ("Harsh Patel", "harsh.patel29@example.com", "9000000029", "B.Tech ECE", 4),
    ("Payal Sahu", "payal.sahu30@example.com", "9000000030", "BCA", 3),

    ("Rajesh Kumar", "rajesh.kumar31@example.com", "9000000031", "B.Tech CSE", 1),
    ("Megha Das", "megha.das32@example.com", "9000000032", "B.Tech IT", 2),
    ("Sanjay Rout", "sanjay.rout33@example.com", "9000000033", "B.Tech ME", 3),
    ("Aditi Sharma", "aditi.sharma34@example.com", "9000000034", "B.Tech CSE", 4),
    ("Naveen Behera", "naveen.behera35@example.com", "9000000035", "B.Tech EEE", 1),
    ("Divya Mohanty", "divya.mohanty36@example.com", "9000000036", "BCA", 2),
    ("Akash Singh", "akash.singh37@example.com", "9000000037", "B.Tech CSE", 3),
    ("Rashmi Das", "rashmi.das38@example.com", "9000000038", "B.Tech ECE", 4),
    ("Suman Nayak", "suman.nayak39@example.com", "9000000039", "B.Tech IT", 1),
    ("Tanya Patel", "tanya.patel40@example.com", "9000000040", "BCA", 2),

    ("Mohit Kumar", "mohit.kumar41@example.com", "9000000041", "B.Tech CSE", 3),
    ("Pallavi Sahu", "pallavi.sahu42@example.com", "9000000042", "B.Tech EEE", 4),
    ("Gaurav Mishra", "gaurav.mishra43@example.com", "9000000043", "B.Tech ME", 1),
    ("Shruti Das", "shruti.das44@example.com", "9000000044", "B.Tech CSE", 2),
    ("Ravi Rout", "ravi.rout45@example.com", "9000000045", "B.Tech ECE", 3),
    ("Kriti Sharma", "kriti.sharma46@example.com", "9000000046", "BCA", 4),
    ("Yash Behera", "yash.behera47@example.com", "9000000047", "B.Tech CSE", 1),
    ("Nandini Mohanty", "nandini.mohanty48@example.com", "9000000048", "B.Tech IT", 2),
    ("Siddharth Singh", "siddharth.singh49@example.com", "9000000049", "B.Tech EEE", 3),
    ("Anjali Nayak", "anjali.nayak50@example.com", "9000000050", "B.Tech CSE", 4),
]


# Add students only if they don't already exist
students = []

for i, data in enumerate(students_data, start=1):

    name, email, phone, course, year = data

    existing = db.query(Student).filter(Student.email == email).first()

    if existing:
        students.append(existing)
        continue

    student = Student(
        name=name,
        email=email,
        phone=phone,
        course=course,
        year=year,
        parent_name=f"Parent of {name}",
        parent_phone=f"800000{i:04d}",
        address=f"Odisha, India - Demo Address {i}",
        admission_date="2026-07-15",
        profile_status="Active",
        photo=f"static/avatars/avatar_{(i % 17) + 1}.jpg"
    )

    db.add(student)
    students.append(student)


db.commit()


# -------------------------------------------------
# 2. ROOM DATA
# -------------------------------------------------

rooms_data = [
    ("A101", 4),
    ("A102", 4),
    ("A103", 4),
    ("A104", 4),
    ("A105", 4),
    ("A106", 4),
    ("A107", 4),
    ("A108", 4),
    ("A109", 4),
    ("A110", 4),

    ("B101", 4),
    ("B102", 4),
    ("B103", 4),
    ("B104", 4),
    ("B105", 4),
]


for room_number, capacity in rooms_data:

    existing = db.query(Room).filter(
        Room.room_number == room_number
    ).first()

    if not existing:
        room = Room(
            room_number=room_number,
            capacity=capacity,
            occupied=0
        )

        db.add(room)


db.commit()


# -------------------------------------------------
# 3. ATTENDANCE DATA
# -------------------------------------------------

for index, student in enumerate(students):

    attendance_date = str(
        date.today() - timedelta(days=index % 5)
    )

    existing = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.date == attendance_date
    ).first()

    if not existing:

        status = "Present" if index % 5 != 0 else "Absent"

        attendance = Attendance(
            student_id=student.id,
            date=attendance_date,
            status=status
        )

        db.add(attendance)


db.commit()


# -------------------------------------------------
# 4. VISITOR DATA
# -------------------------------------------------

for index, student in enumerate(students[:20], start=1):

    visit_date = str(date.today())

    visitor = Visitor(
        student_id=student.id,
        visitor_name=f"Visitor {index}",
        relation="Parent",
        phone=f"700000{index:04d}",
        visit_date=visit_date,
        in_time="10:00 AM",
        out_time="12:00 PM",
        purpose="Student visit"
    )

    db.add(visitor)


db.commit()


# -------------------------------------------------
# 5. GATE PASS DATA
# -------------------------------------------------

for index, student in enumerate(students[:15], start=1):

    gate_pass = GatePass(
        student_id=student.id,
        reason="Personal work",
        pass_date=str(date.today()),
        out_time="04:00 PM",
        in_time="07:00 PM",
        status="Returned"
    )

    db.add(gate_pass)


db.commit()


# -------------------------------------------------
# 6. COMPLAINT DATA
# -------------------------------------------------

complaint_types = [
    "Room Maintenance",
    "Electricity",
    "Water Supply",
    "Internet",
    "Cleanliness"
]

statuses = [
    "Pending",
    "In Progress",
    "Resolved"
]


for index, student in enumerate(students[:20]):

    complaint = Complaint(
        student_id=student.id,
        complaint_type=complaint_types[index % len(complaint_types)],
        description=f"Demo complaint regarding hostel facilities - Record {index + 1}",
        complaint_date=str(date.today()),
        status=statuses[index % len(statuses)]
    )

    db.add(complaint)


db.commit()


# -------------------------------------------------
# 7. NOTICE BOARD DATA
# -------------------------------------------------

notices = [
    (
        "Hostel Orientation",
        "Hostel orientation program for newly admitted students.",
        "General"
    ),
    (
        "Hostel Fee Reminder",
        "Students are requested to complete hostel fee payment.",
        "Fee"
    ),
    (
        "Cleanliness Drive",
        "A hostel cleanliness drive will be conducted this week.",
        "Event"
    ),
    (
        "Attendance Notice",
        "All students must maintain minimum hostel attendance.",
        "Important"
    ),
    (
        "Visitor Timing",
        "Visitors are allowed during the designated visiting hours.",
        "General"
    ),
]


for title, description, notice_type in notices:

    notice = Notice(
        title=title,
        description=description,
        notice_date=str(date.today()),
        notice_type=notice_type
    )

    db.add(notice)


db.commit()


# -------------------------------------------------
# FINISH
# -------------------------------------------------

db.close()

print("----------------------------------------")
print("HOSTEL HUB DEMO DATA INSERTED")
print("----------------------------------------")
print("50 students added/verified")
print("15 rooms added/verified")
print("Attendance records added")
print("Visitor records added")
print("Gate pass records added")
print("Complaint records added")
print("Notice board records added")
print("----------------------------------------")
