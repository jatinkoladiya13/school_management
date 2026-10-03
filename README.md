# School Management System

A backend REST API for school operations, built with Django 4.1, Django REST Framework, and MongoDB through Djongo. It covers user accounts with JWT login and email OTP password reset, roles and CRUD permission sets, standards, subjects, classes, students, teachers, student and teacher attendance, timetables, exams, and graded results. It also includes MongoDB aggregation reports and a Celery Beat job that emails teachers before their classes start.

## Highlights

- Custom `User` model keyed by MongoDB `ObjectId`, with email as the login field
- JWT access and refresh tokens (Simple JWT), with token blacklisting on logout
- Email OTP flow for verifying a user and resetting the password
- Roles (`Rolle`) and permission sets (`Permission`) with create, update, delete, and view flags
- Standards, subjects, school classes, students, and teachers
- Daily student attendance recorded per teacher as a single document with embedded entries
- Teacher attendance with a reason field for absences
- Weekly timetable with lookup of the lecture running at a given time
- Exams with subject lists, and results with automatic totals, percentage, and grade
- MongoDB aggregation pipelines for student and teacher attendance reports
- Result filtering by pass status, subject, and student
- Celery Beat task that sends class reminder emails every minute
- Custom DRF exception handler that returns a consistent `status` / `detail` / `code` error body

## Technology

| Area | Technology |
| --- | --- |
| Framework | Django 4.1.13, Django REST Framework 3.15.2 |
| Database | MongoDB through Djongo 1.3.6 and PyMongo 3.12.1 |
| Authentication | JWT with `djangorestframework-simplejwt` 5.3.1 and its token blacklist app |
| Background jobs | Celery with a Redis broker (`redis://localhost:6379/0`) and Celery Beat |
| Email | Django SMTP backend (Gmail SMTP, port 587, TLS) |
| PDF | ReportLab (`app/result_pdf.py`) |
| Configuration | `django-dotenv` loads `.env` from `manage.py` |

> **MongoDB is required.** The project does not use SQLite or PostgreSQL. The Django ORM talks to MongoDB through Djongo, and the aggregation endpoints query MongoDB directly with PyMongo.

## Architecture

```text
Client
  |
  v
Django REST API (app/) --------- Djongo ORM ----------+
  |                                                   |
  +-- Aggregation views -------- PyMongo pipelines ---+--> MongoDB "school_management"
  |
  +-- OTP emails --------------- Gmail SMTP

Celery Beat (every 60 s)
  |
  v
Celery worker -- check_timetable_task --> reads Timetable --> SMTP reminder to teacher
  ^
  |
Redis broker (localhost:6379/0)
```

## Project Structure

```text
school_management/
├── app/
│   ├── migrations/           Initial migration for all models
│   ├── common_function.py    ObjectId-to-string conversion and grade calculation
│   ├── cron.py               Unused reminder command draft (not registered)
│   ├── customauthentication.py  JWT authentication that also checks logout state
│   ├── email.py              OTP generation and email sending
│   ├── exceptions.py         Custom DRF exception handler
│   ├── models.py             All data models
│   ├── permission.py         Custompermission and CustomPermissionAdmin classes
│   ├── result_pdf.py         ReportLab result report generator
│   ├── serializers.py        DRF serializers with ObjectId handling
│   ├── service.py            PyMongo client used by aggregation views
│   ├── tasks.py              Celery task for class reminder emails
│   ├── url.py                All API routes
│   └── views.py              API views
├── school_management/
│   ├── celery.py             Celery application
│   ├── check_timetable.py    Unused management command draft (not registered)
│   ├── settings.py           Django, MongoDB, email, Celery, and JWT settings
│   ├── urls.py               Root URLconf (admin and app routes)
│   ├── asgi.py
│   └── wsgi.py
├── manage.py                 Loads .env before running Django commands
└── requirements.txt
```

## Data Model

All models use a MongoDB `ObjectId` as the `_id` primary key. API requests and responses pass related objects as `ObjectId` strings.

| Model | Key fields |
| --- | --- |
| `Rolle` | `rolle_name` |
| `Permission` | `create`, `update`, `delete_permission`, `view` (string flags, `"true"` grants access) |
| `User` | `email` (unique, login field), `username` (unique), `mobile_number`, `otp`, `rolle` (FK), `permission` (FK) |
| `Standard` | `student_stander` (unique) |
| `Subject` | `subject` (unique) |
| `SchoolClass` | `class_name` (unique) |
| `Student` | `user` (one-to-one), `roll_number`, `standard`, `school_class` |
| `Teacher` | `user` (one-to-one), `qualification`, `subject` (array reference), `standard` (array reference), `school_class` |
| `Attendance` | `teacher`, `date` (auto), `attendance` (list of `{student, today_present, reason}`); unique per teacher and date |
| `TeacherAttendance` | `teacher`, `date` (auto), `today_present`, `reason` |
| `Timetable` | `school_class`, `subject`, `teacher`, `day_of_week` (`Monday` to `Sunday`), `start_time`, `end_time` |
| `Exam` | `exam_name`, `standard`, `created_by` (user), `attendance`, `total_mark` (per subject), `exam_date`, `subjects` (list of subject IDs), `start_time`, `end_time` |
| `Result` | `exam`, `student`, `marks_obtained` (list of `{subject, marks}`), `total_marks`, `percentage`, `grade`, `created_at` |

### Model rules

- A `Student` can only be saved for a user whose role name is `student`.
- A `Teacher` can only be saved for a user whose role name is `teacher`.
- When attendance is recorded, every student must belong to the teacher's `school_class`, and a student cannot appear twice in one entry.
- A student's roll number must be unique within a class.

## Roles and Permissions

Roles are stored in the `Rolle` collection and are assigned to users by `ObjectId`. The code relies on three role names:

| Role name | Used by |
| --- | --- |
| `admin` | `CustomPermissionAdmin` grants access only to users with this role |
| `teacher` | Required for a user linked to a `Teacher` profile |
| `student` | Required for a user linked to a `Student` profile |

Each user also references a `Permission` document. `Custompermission` maps HTTP methods to its flags:

| HTTP method | Permission field that must equal `"true"` |
| --- | --- |
| `POST` | `create` |
| `PUT` | `update` |
| `GET` | `view` |
| `DELETE` | `delete_permission` |

> **Current enforcement:** `Custompermission` and `CustomPermissionAdmin` are defined in `app/permission.py`, but their use in the views is commented out. Only `GET /userget/` and `PUT`/`DELETE /userputordeleteview/` require authentication (JWT plus `IsAuthenticated`). All other endpoints are open, because no default authentication or permission classes are set in `REST_FRAMEWORK`.

## Authentication

Send the access token as a bearer token:

```http
Authorization: Bearer <access_token>
```

- `POST /userlogin/` authenticates with email and password and returns `refresh` and `access` tokens.
- The access token is valid for 20 minutes and the refresh token for 1 day.
- `POST /api/token/refresh/` exchanges a refresh token for a new access token.
- `POST /userlogout/` blacklists the refresh token and records it against the user. `CustomJWTAuthentication` rejects requests from a user who has a recorded logout token. The next successful login clears it.

## OTP Password Reset Flow

1. `POST /sendotp/` with `email` generates a random 4-digit OTP, emails it, and stores it on the user.
2. `POST /verifyotp/` with `email` and `otp` checks it. On success the stored OTP is set to `1`, which marks the user as verified.
3. `POST /changepassword/` with `email` and `password` sets the new password only if the user is verified (`otp == 1`). The OTP is then reset to `0`.

## API Endpoints

All routes are mounted at the site root. The paths below are exact, including their spelling. `<pk>` and `<_id>` are MongoDB `ObjectId` strings.

Success responses generally use `{"status": "200", "msg": ...}`, with list data returned in `msg`.

### Accounts

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/usercreate/` | Public | Register a user (`email`, `username`, `password`, `mobile_number`, `rolle`, `permission`). Rejects a duplicate email or username |
| `GET` | `/userget/` | JWT | Return the authenticated user |
| `POST` | `/userlogin/` | Public | Log in with `email` and `password`, and return JWT tokens |
| `PUT` | `/userputordeleteview/` | JWT | Update the authenticated user |
| `DELETE` | `/userputordeleteview/` | JWT | Delete the authenticated user |
| `POST` | `/userlogout/` | Public | Blacklist the given `refresh_token` |
| `POST` | `/api/token/refresh/` | Public | Get a new access token from `refresh` |
| `POST` | `/sendotp/` | Public | Email an OTP to `email` |
| `POST` | `/verifyotp/` | Public | Verify `email` and `otp` |
| `POST` | `/changepassword/` | Public | Set a new `password` for a verified `email` |

### Roles and Permissions

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/creatorgetroll/` | List roles |
| `POST` | `/creatorgetroll/` | Create a role (`rolle_name`, must be unique) |
| `GET` | `/udrolleview/<pk>/` | Get a role name |
| `PUT` | `/udrolleview/<pk>/` | Update a role |
| `DELETE` | `/udrolleview/<pk>/` | Delete a role |
| `GET` | `/permissioncreateview/` | List permission sets |
| `POST` | `/permissioncreateview/` | Create a permission set. An identical combination is rejected |
| `GET` | `/retriveUpdateDeleteRolle/<_id>/` | Retrieve a permission set |
| `PUT` | `/retriveUpdateDeleteRolle/<_id>/` | Update a permission set |
| `DELETE` | `/retriveUpdateDeleteRolle/<_id>/` | Delete a permission set |

### Standards and Subjects

These routes are registered with a DRF `DefaultRouter` under `/standerorsubjectview/`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/standerorsubjectview/` | Router root listing the two resources |
| `GET` | `/standerorsubjectview/stander/` | List standards |
| `POST` | `/standerorsubjectview/stander/` | Create a standard (`student_stander`) |
| `PUT` | `/standerorsubjectview/stander/<pk>/` | Update a standard |
| `GET` | `/standerorsubjectview/subject/` | List subjects |
| `POST` | `/standerorsubjectview/subject/` | Create a subject (`subject`) |
| `PUT` | `/standerorsubjectview/subject/<pk>/` | Update a subject |

### School Classes

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/schoolclassview/` | List classes |
| `POST` | `/schoolclassview/` | Create a class (`class_name`) |
| `PUT` | `/schoolUDview/<pk>/` | Update a class |
| `DELETE` | `/schoolUDview/<pk>/` | Delete a class |

### Students

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/studentview/` | List students |
| `POST` | `/studentview/` | Create a student profile (`user`, `standard`, `school_class`, `roll_number`) |
| `PUT` | `/studeudview/<pk>/` | Update a student |
| `DELETE` | `/studeudview/<pk>/` | Delete a student |

### Teachers

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/teacherview/` | List teachers |
| `POST` | `/teacherview/` | Create a teacher profile (`user`, `qualification`, `school_class`, `subject` list, `standard` list) |
| `PUT` | `/teacherUDview/<pk>/` | Update a teacher. The subject and standard lists are replaced |
| `DELETE` | `/teacherUDview/<pk>/` | Delete a teacher |

### Student Attendance

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/attendanceveiw/` | List attendance entries |
| `POST` | `/attendanceveiw/` | Record today's attendance for a teacher's class |
| `PUT` | `/attendanceudveiw/<pk>/` | Replace an attendance entry |
| `DELETE` | `/attendanceudveiw/<pk>/` | Delete an attendance entry |
| `PUT` | `/attendancemenullyupdate/<pk>/` | Update one student (`student`, `today_present`, `reason`) inside an attendance entry |
| `POST` | `/AttendanceAggregationPipelineView/` | Student attendance aggregation report (see below) |

### Teacher Attendance

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/teacherattendance/` | List teacher attendance |
| `POST` | `/teacherattendance/` | Record a teacher's attendance (`teacher`, `today_present`, `reason`) |
| `PUT` | `/teacherattendanceUD/<pk>/` | Update a teacher attendance record |
| `DELETE` | `/teacherattendanceUD/<pk>/` | Delete a teacher attendance record |
| `POST` | `/teacherattendanceAggPip/` | Teacher attendance aggregation report (see below) |

### Timetable

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/timetableview/` | List lectures |
| `POST` | `/timetableview/` | Create a lecture (`school_class`, `subject`, `teacher`, `day_of_week`, `start_time`, `end_time`). Duplicate slots for a class are rejected |
| `PUT` | `/timetableUDview/<pk>/` | Update a lecture |
| `DELETE` | `/timetableUDview/<pk>/` | Delete a lecture |
| `POST` | `/timelectureAggPip/` | Find lectures running at a given `time` (`HH:MM:SS`) on a given `day`. Without both values, returns all lectures |

### Exams and Results

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/examview/` | List exams |
| `POST` | `/examview/` | Create an exam (`exam_name`, `standard`, `created_by`, `attendance`, `total_mark`, `exam_date`, `subjects`, `start_time`, `end_time`) |
| `PUT` | `/examUDView/<pk>/` | Update an exam |
| `DELETE` | `/examUDView/<pk>/` | Delete an exam |
| `GET` | `/resultview/` | List results |
| `POST` | `/resultview/` | Create a result (`exam`, `student`, `marks_obtained`). Allows only one result per student per exam, and only the exam's subjects |
| `PUT` | `/resultUDView/<pk>/` | Update a result and recalculate the percentage and grade |
| `DELETE` | `/resultUDView/<pk>/` | Delete a result |
| `POST` | `/resultfilter/` | Filter results (see below) |

### Administration

| Method | Path | Description |
| --- | --- | --- |
| Any | `/admin/` | Django admin site (no models are registered in `app/admin.py`) |

## Reports and Calculations

### Student attendance aggregation

`POST /AttendanceAggregationPipelineView/` runs a PyMongo pipeline on the `app_attendance` collection:

1. `$unwind` the embedded `attendance` list.
2. `$match` on `teacher_id`, a date range from `start_date` to `end_date` (inclusive, `YYYY-MM-DD`), and, if given, `attendance.today_present` (`"True"` or `"False"`).
3. `$group` by teacher, date, and entry `_id`. Each group returns `presentStudents` (the list of `{student, today_present}`) and `attendanceCount` (the number of matching students).

### Teacher attendance aggregation

`POST /teacherattendanceAggPip/` runs a `$match` on the `app_teacherattendance` collection, using the same `teacher_id`, `start_date`, `end_date`, and optional `present` filters. It then runs a `$group` that returns one `_id` object per record, containing `teacher`, `date`, `_id`, and `today_present`.

### Result grading

When a result is created or updated:

- `total_marks` is the sum of `marks_obtained[].marks`.
- `percentage` is `total_marks * 100 / (exam.total_mark * number of exam subjects)`.
- `grade` is assigned from the percentage:

| Percentage | Grade |
| --- | --- |
| 90 and above | `A1` |
| 80 to 89 | `A2` |
| 70 to 79 | `B1` |
| 60 to 69 | `B2` |
| 50 to 59 | `C1` |
| 40 to 49 | `C2` |
| 33 to 39 | `D` |
| 20 to 32 | `E1` |
| Below 20 | `E2` |

### Result filter

`POST /resultfilter/` accepts any combination of these fields:

- `check_status`: `"Pass"` keeps grades `A1` to `D`.
- `subject`: a subject name. It keeps results that include marks for that subject.
- `student_name`: the student user's `username`.

The response has the shape `{"status": "200", "data": [...]}`.

### Result PDF

`app/result_pdf.py` defines `create_result_pdf(student_info, exam_info, marks_obtained)`, which builds an A4 "Result Report" with ReportLab. The report has student and exam details and a subject / marks / grade table. The module calls this function with hard-coded sample data when it is imported. Because `app/views.py` imports it, `result.pdf` is written to the working directory each time the app loads. No API endpoint returns the PDF.

## Scheduled Jobs

Celery Beat is configured in `settings.py`:

| Schedule name | Task | Interval |
| --- | --- | --- |
| `check-timetable-every-minute` | `app.tasks.check_timetable_task` | Every 60 seconds |

The task finds timetable entries whose `start_time` falls within the next five minutes. For each one, it sends a reminder email over SMTP to the teacher's address, using the `EMAIL_USER` and `EMAIL_PASS` credentials.

`django-cron` is listed in `requirements.txt`, but no cron classes are configured. `app/cron.py` and `school_management/check_timetable.py` are drafts that are not registered as management commands.

## Example Requests

Register a user:

```http
POST /usercreate/
Content-Type: application/json

{
  "email": "teacher1@example.com",
  "username": "teacher1",
  "password": "StrongPass123",
  "mobile_number": "9876543210",
  "rolle": "66a0f1c2e4b0a1b2c3d4e5f6",
  "permission": "66a0f1c2e4b0a1b2c3d4e5f7"
}
```

Record student attendance for today:

```http
POST /attendanceveiw/
Content-Type: application/json

{
  "teacher": "66a0f2d3e4b0a1b2c3d4e600",
  "attendance": [
    { "student": "66a0f3e4e4b0a1b2c3d4e610", "today_present": "True" },
    { "student": "66a0f3e4e4b0a1b2c3d4e611", "today_present": "False", "reason": "Sick leave" }
  ]
}
```

Create a result:

```http
POST /resultview/
Content-Type: application/json

{
  "exam": "66a0f4f5e4b0a1b2c3d4e620",
  "student": "66a0f3e4e4b0a1b2c3d4e610",
  "marks_obtained": [
    { "subject": "66a0f1a1e4b0a1b2c3d4e501", "marks": "85" },
    { "subject": "66a0f1a1e4b0a1b2c3d4e502", "marks": "92" }
  ]
}
```

Student attendance report:

```http
POST /AttendanceAggregationPipelineView/
Content-Type: application/json

{
  "teacher_id": "66a0f2d3e4b0a1b2c3d4e600",
  "start_date": "2024-07-01",
  "end_date": "2024-07-31",
  "present": "True"
}
```

## Local Requirements

- Python 3 (the existing virtual environment uses Python 3.13)
- MongoDB server on port `27017`, with a user that authenticates against the `admin` database using SCRAM-SHA-1
- Redis on `localhost:6379`, only if you run Celery
- A Gmail account or app password for OTP and reminder emails

## Getting Started

### 1. Create a virtual environment and install dependencies

```powershell
cd school_management
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The code also imports packages that are not listed in `requirements.txt`. Install them separately:

```powershell
pip install reportlab celery redis
```

`reportlab` is required to start the server, because `app/views.py` imports `app/result_pdf.py`.

### 2. Configure environment variables

Create a `.env` file in the project root, next to `manage.py`. It is excluded by `.gitignore`. `manage.py` loads it through `django-dotenv`.

| Variable | Used for |
| --- | --- |
| `MONGO_HOST` | MongoDB host for Djongo and the PyMongo aggregation client |
| `MONGO_PASSWORD` | MongoDB password |
| `EMAIL_USER` | SMTP username, used for OTP emails and Celery reminders |
| `EMAIL_PASS` | SMTP password or app password |

```env
MONGO_HOST=localhost
MONGO_PASSWORD=replace-me
EMAIL_USER=your-address@gmail.com
EMAIL_PASS=replace-with-app-password
```

The MongoDB database name (`school_management`), port, username, and auth settings are hard-coded in `school_management/settings.py`. Edit the `DATABASES` block to match your MongoDB user.

### 3. Apply migrations

```powershell
python manage.py migrate
```

### 4. Seed roles and permissions

Before registering users, create the roles (`admin`, `teacher`, `student`) through `POST /creatorgetroll/` and at least one permission set through `POST /permissioncreateview/`. Registration requires both `rolle` and `permission` IDs.

### 5. Run the development server

```powershell
python manage.py runserver
```

The API is served at `http://127.0.0.1:8000/`.

### 6. Run Celery for class reminders (optional)

Start Redis, then run the worker and the scheduler in separate terminals:

```powershell
celery -A school_management worker -l info --pool=solo
celery -A school_management beat -l info
```

Celery does not start through `manage.py`, so `.env` is not loaded automatically for these processes. `app/tasks.py` loads a `.env` file from a hard-coded absolute path (`school_management\school_management\.env`). Make sure the variables are available to the worker.

## Error Responses

`app.exceptions.custom_exception_handler` formats DRF errors:

- Authentication failures: `{"status": 401, "detail": "...", "code": "authentication_failed"}`
- Invalid or expired tokens: HTTP 400 with `"code": "token_not_valid"`
- Any other DRF exception: HTTP 500 with `"code": "unknown_error"`

Validation errors from serializers are returned directly by the views, usually as `{"status": "400", "msg": <errors>}`.
