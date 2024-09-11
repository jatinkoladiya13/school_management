from djongo import models
from django.contrib.auth.models import AbstractUser
from bson import ObjectId

# Create your models here.


class Rolle(models.Model):
    id= None
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    rolle_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.rolle_name}'  

class Permission(models.Model):
    id=None
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)
    create = models.CharField(max_length=255, blank=True, null=True)
    update = models.CharField(max_length=255, blank=True, null=True)
    delete_permission = models.CharField(max_length=255, blank=True, null=True)
    view = models.CharField(max_length=255, blank=True, null=True)



class User(AbstractUser):
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    id = None
    last_login = None
    is_superuser = None
    first_name = None
    last_name = None
    is_staff = None
    is_active = None
    date_joined = None
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(unique=True,max_length=255, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    otp = models.IntegerField(null=True, blank=True)
    rolle = models.ForeignKey(Rolle,on_delete=models.CASCADE, null=True)
    permission = models.ForeignKey(Permission,on_delete=models.CASCADE, null=True )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'mobile_number']
    
    def __str__(self) -> str:
        return f'{self.username}'
    
class Standard(models.Model):
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    id = None
    student_stander = models.CharField(unique=True,max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.student_stander}'
    
class Subject(models.Model):
    id = None
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    subject = models.CharField(unique=True,max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.subject}'    

class SchoolClass(models.Model):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)
    class_name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.class_name

class Student(models.Model):
    id=None
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    standard = models.ForeignKey(Standard, on_delete= models.CASCADE)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, null=True)
    
    def __str__(self) -> str:
        return f'{self.user.username} (Student)'
    
    def save(self, *args, **kwargs):
        if self.user.rolle.rolle_name != 'student':
            raise ValueError("Only users with role 'student' can be associated with a Student instance.")
        return super().save(*args, **kwargs)
    
class Teacher(models.Model):
    id=None 
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    qualification = models.CharField(max_length=100, blank=True, null=True)
    subject = models.ArrayReferenceField(to= 'Subject', on_delete=models.CASCADE,)
    standard = models.ArrayReferenceField(to= 'Standard', on_delete=models.CASCADE,) 
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE,  null=True)

    def __str__(self) -> str:
        return f'{self.user.username} (Teacher)'

    def save(self, *args, **kwargs):
        if self.user.rolle.rolle_name != 'teacher':
            raise ValueError("Only users with role 'Teacher' can be associated with a Teacher instance.")
        
        return super().save(*args, **kwargs)  


class Attendance(models.Model):
    id=None 
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,  null=True)
    date = models.DateField(auto_now_add=True)
    attendance = models.JSONField()

    class Meta:
        unique_together = ['teacher', 'date']

    def __str__(self):
        
        return f"AttendanceEntery for {self.teacher} on {self.date}" 

class TeacherAttendance(models.Model):
    id=None
    _id = models.ObjectIdField(default=ObjectId,  primary_key=True,)
    date = models.DateField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,  null=True)      
    today_present = models.BooleanField(null=True)
    reason =  models.CharField(max_length=255, blank=True, null=True)


class Timetable(models.Model):
    id=None
    _id = models.ObjectIdField(default = ObjectId, primary_key = True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE,  null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,  null=True) 
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE,  null=True)
    day_of_week = models.CharField(max_length=10, blank=True, null=True, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.school_class.class_name} - {self.subject.subject} ({self.day_of_week} {self.start_time} - {self.end_time})'
    
class Exam(models.Model):
    id = None
    _id = models.ObjectIdField(default = ObjectId, primary_key = True)
    exam_name = models.CharField(max_length=255, blank=True, null=True)
    standard  = models.ForeignKey(Standard, on_delete= models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, null=True)
    total_mark =  models.IntegerField(null=True, blank=True)
    exam_date = models.DateField()
    subjects  = models.JSONField()
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)

    def __str__(self) -> str:
        return f'{self.created_by} - {self.standard} - {self.attendance} ({self.exam_name} {self.exam_date} {self.total_mark})'
    
class Result(models.Model):
    id = None
    _id = models.ObjectIdField(default = ObjectId, primary_key = True)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student  = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.JSONField()
    total_marks = models.IntegerField()
    percentage = models.FloatField()
    grade = models.CharField(max_length=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f'{self.student} - {self.exam} ({self.total_marks})'
