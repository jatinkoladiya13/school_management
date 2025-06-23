# School Management System – Django REST API

A backend-only Django REST API for managing school operations such as users, roles, students, teachers, subjects, classes, attendance, timetable, and exam results.

## Features (API Endpoints Overview)

### Authentication & User Management
- `POST /usercreate/` – Register user
- `GET /userget/` – Get all users
- `POST /userlogin/` – User login with token generation
- `PUT/DELETE /userputordeleteview/` – Update or delete user
- `POST /userlogout/` – Logout user
- `POST /sendotp/` – Send OTP for verification
- `POST /verifyotp/` – Verify OTP
- `POST /changepassword/` – Change user password

### Roles & Permissions
- `GET /creatorgetroll/` – Get all roles
- `PUT/DELETE /udrolleview/<id>/` – Update/Delete role by ID
- `POST /permissioncreateview/` – Create permission
- `PUT/DELETE /retriveUpdateDeleteRolle/<id>/` – Update/Delete permission

---

### Academic: Standards, Subjects
- `GET/POST /stander/` – Manage class standards (grade levels)
- `GET/POST /subject/` – Manage subjects

---

### Students
- `GET/POST /studentview/` – Add or list students
- `PUT/DELETE /studeudview/<id>/` – Update/Delete student

---

### Teachers
- `GET/POST /teacherview/` – Add or list teachers
- `PUT/DELETE /teacherUDview/<id>/` – Update/Delete teacher
  
---

### Classes
- `GET/POST /schoolclassview/` – Add or list classes
- `PUT/DELETE /schoolUDview/<id>/` – Update/Delete class info

---

### Attendance

#### Student Attendance
- `GET/POST /attendanceveiw/` – Add or get attendance
- `PUT/DELETE /attendanceudveiw/<id>/` – Update/Delete attendance
- `PATCH /attendancemenullyupdate/<id>/` – Manually update attendance
- `GET /AttendanceAggregationPipelineView/` – Aggregate student attendance

#### Teacher Attendance
- `GET/POST /teacherattendance/` – Add or get teacher attendance
- `PUT/DELETE /teacherattendanceUD/<id>/` – Update/Delete teacher attendance
- `GET /teacherattendanceAggPip/` – Aggregate teacher attendance

---

### Timetable
- `GET/POST /timetableview/` – Add or list lectures
- `PUT/DELETE /timetableUDview/<id>/` – Update/Delete lecture
- `GET /timelectureAggPip/` – Aggregate lecture data

---

### Exams & Results
- `GET/POST /examview/` – Create or list exams
- `PUT/DELETE /examUDView/<id>/` – Update/Delete exam
- `GET/POST /resultview/` – Create or list student results
- `PUT/DELETE /resultUDView/<id>/` – Update/Delete result
- `GET /resultfilter/` – Filter results by parameters

---

## Tech Stack

- **Backend**: Django, Django REST Framework and ORM Djongo 
- **Auth**: JWT (via `rest_framework_simplejwt`)
- **Database**: MongoDB 
- **API Testing**: Postman / Swagger (optional)

  

