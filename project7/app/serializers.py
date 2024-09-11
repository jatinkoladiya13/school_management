from rest_framework import serializers
from app.models import User, Rolle, Permission, Standard, Subject, SchoolClass, Student,  Teacher, Attendance, TeacherAttendance, Timetable, Exam, Result
from bson import ObjectId
from django.shortcuts import get_object_or_404
from app.common_function import calculate_grade

class UserSerializer(serializers.ModelSerializer): 

    class Meta:
        model = User
        fields =['_id', 'password', 'email', 'mobile_number', 'username', 'rolle', 'permission']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = User(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            mobile_number=validated_data.get('mobile_number'),
            otp=validated_data.get('otp', 0),
            rolle = validated_data.get('rolle'),
            permission = validated_data.get('permission')
        )
        
        user.set_password(validated_data.get('password'))
        user.save()
        return user
    
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.mobile_number = validated_data.get('mobile_number', instance.mobile_number)
        instance.username = validated_data.get('username', instance.username)
        instance.otp =  validated_data.get('otp', instance.otp)
    

        rolle_data = validated_data.get('rolle')
        if rolle_data:
            try:
                rolle_instance = Rolle.objects.get(_id=rolle_data._id)
            except Rolle.DoesNotExist:
                raise serializers.ValidationError("Rolle matching query does not exist.")
            instance.rolle = rolle_instance

        # Handle permission field
        permission_data = validated_data.get('permission')
        if permission_data:
            try:
                permission_instance = Permission.objects.get(_id=permission_data._id)
            except Permission.DoesNotExist:
                raise serializers.ValidationError("Permission matching query does not exist.")
            instance.permission = permission_instance 
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()
        return instance
    
    def to_internal_value(self, data):
        data["rolle"] = ObjectId(data["rolle"])
        data["permission"] = ObjectId(data["permission"])
        return super().to_internal_value(data)    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['rolle'] = str(instance.rolle._id)
        representation['permission'] = str(instance.permission._id)
        return representation 
    

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.IntegerField()


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(required = True)

class RolleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rolle
        fields = ['_id', 'rolle_name']
        ordering = "_id"

    def validate(self, attrs):
        existing_rolle = Rolle.objects.filter(rolle_name=attrs['rolle_name']).count() > 0
        if existing_rolle:
            raise serializers.ValidationError("Rolle with this rolle_name already exists.")
        
        return attrs    

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['_id', 'create', 'update', 'delete_permission', 'view']
        ordering = "_id"
     

class StanderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ['_id', 'student_stander']
        ordering = "_id"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['_id', 'subject']
        ordering = "_id"            

class SchoolClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolClass
        fields = ['_id', 'class_name']
        ordering = "_id"
        
class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['_id', 'user', 'roll_number', 'standard', 'school_class']
        ordering = "_id"        

    def to_internal_value(self, data):
        if 'user' in data:
            data["user"] = ObjectId(data["user"])
        if 'standard' in data:
            data["standard"] = ObjectId(data["standard"])
        if 'school_class' in data:
            data["school_class"] = ObjectId(data["school_class"])
        return data    
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['user'] = str(instance.user._id)
        representation['standard'] = str(instance.standard._id)
        representation['school_class'] = str(instance.school_class._id)
        return representation     
    
    def create(self, validated_data):
        user_id = validated_data.pop('user')
        standard_id = validated_data.pop('standard')
        school_class_id = validated_data.pop('school_class')
        roll_number  = validated_data.pop('roll_number')

        user = User.objects.get(_id=ObjectId(user_id)) 
        standard = Standard.objects.get(_id=ObjectId(standard_id))
        school_class = SchoolClass.objects.get(_id=ObjectId(school_class_id)) 
      
        student = Student(user=user,  standard=standard, school_class=school_class, roll_number=roll_number)
        student.save()
      
        return student
    
    def update(self, instance, validated_data):
        user_id = validated_data.get('user', instance.user)
        standard_id = validated_data.get('standard', instance.standard)
        school_class_id = validated_data.get('school_class', instance.school_class)
        roll_number  = validated_data.get('roll_number', instance.roll_number)
        
        user = User.objects.get(_id=ObjectId(user_id)) 
        standard = Standard.objects.get(_id=ObjectId(standard_id))
        school_class = SchoolClass.objects.get(_id=ObjectId(school_class_id)) 
        
        instance.roll_number = roll_number
        instance.user = user
        instance.standard = standard
        instance.school_class = school_class
        
        instance.save()
        return  instance
    
class  TeacherSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    school_class = serializers.CharField()   
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=True)
    standard = serializers.PrimaryKeyRelatedField(queryset=Standard.objects.all(), many=True)
    class Meta:
        model = Teacher
        fields = ['_id', 'user', 'subject', 'standard', 'qualification', 'school_class']

    def to_internal_value(self, data):
        if 'user' in data:
            data['user'] = ObjectId(data['user'])
         
        if 'school_class' in data:
            data['school_class'] = ObjectId(data['school_class']) 

        if 'subject' in data:
            data['subject'] = [ObjectId(subject_id) for subject_id in data['subject']]
       
        if 'standard' in data:
            data['standard'] = [ObjectId(standard_id) for standard_id in data['standard']]

        return data

    def create(self, validated_data):
        subject_data = validated_data.pop('subject', [])
        standard_data = validated_data.pop('standard', [])
        qualification = validated_data.pop('qualification', None)
        user_id = validated_data.pop('user')
        school_class_id = validated_data.pop('school_class')
    
        user = User.objects.get(_id=ObjectId(user_id)) 
        school_class = SchoolClass.objects.get(_id=ObjectId(school_class_id)) 

        subjects = [get_object_or_404(Subject, _id=ObjectId(sub_id)) for sub_id in subject_data]  
        standards = [get_object_or_404(Standard, _id=ObjectId(std_id)) for std_id in standard_data]
       
        teacher = Teacher.objects.create(user=user, qualification=qualification, school_class=school_class, **validated_data)
        teacher.subject.add(*subjects)
        teacher.standard.add(* standards)
       
        teacher.save()

        return teacher
    
    def update(self, instance, validated_data):
        instance.qualification = validated_data.get('qualification', instance.qualification)
        instance.school_class = validated_data.get('school_class', instance.school_class)

        user_id = validated_data.get('user')
        if user_id:
            instance.user = User.objects.get(_id=ObjectId(user_id))
        
        subject_data =validated_data.get('subject', [])
        subjects = [get_object_or_404(Subject, _id=ObjectId(sub_id)) for sub_id in subject_data]
        instance.subject.clear()
        instance.subject.add(*subjects)
 
        standard_data = validated_data.get('standard', [])
        standards = [get_object_or_404(Standard, _id=ObjectId(std_id)) for std_id in standard_data]
        instance.standard.clear()
        instance.standard.add(*standards)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['user'] = str(instance.user._id)
        representation['school_class'] = str(instance.school_class)
        representation['subject'] = [str(subject._id) for subject in instance.subject.all()]
        representation['standard'] = [str(standard._id) for standard in instance.standard.all()]
        return representation
    
class AttendanceEnterySerializer(serializers.ModelSerializer):
    teacher = serializers.CharField()
    attendance = serializers.ListField(child=serializers.DictField()) 
    class Meta:
        model = Attendance
        fields = ['_id', 'teacher', 'date', 'attendance']
    
    def to_internal_value(self, data):
        if 'teacher' in data:
            data['teacher'] = ObjectId(data['teacher'])
        
        attendance_data = []
        student_ids = set()
        if 'attendance' in data:
            teacher = Teacher.objects.get(_id=data['teacher'])
            for attendance in data['attendance']: 

                student_id = ObjectId(attendance["student"])
                
                student = Student.objects.get(_id=student_id)
                if teacher.school_class  != student.school_class:
                    raise serializers.ValidationError({"student": "This student is not allowed this class."})
                
                if student_id not in student_ids:
                    attendance_data.append({
                        "student": student_id,
                        "today_present": attendance["today_present"] == "True",
                        "reason": attendance.get("reason", "")
                    })
                else:
                    raise serializers.ValidationError({"student": "Duplicate student entry is not allowed."})    
            
            student_ids.clear()
            data['attendance']  = attendance_data   
            
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['teacher'] = str(instance.teacher._id)
        representation['date'] = str(instance.date)
        representation['attendance'] = [
            {
                'student': str(attendance['student']),
                'today_present': attendance['today_present'],
                'reason': attendance.get('reason', "")

            }
            for attendance in instance.attendance
        ]
        return representation
    
    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher')
        teacher = Teacher.objects.get(_id=ObjectId(teacher_id)) 
        attendance_entry = Attendance.objects.create(teacher=teacher, **validated_data)
        attendance_entry.save()
        return attendance_entry
    
    def update(self, instance, validated_data):
        teacher_id = validated_data.get('teacher', instance.teacher)
        teacher = Teacher.objects.get(_id=ObjectId(teacher_id))
        instance.teacher = teacher
        instance.attendance = validated_data.get('attendance', instance.attendance)
        
        instance.save()
        return instance
    
class TeacherAttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherAttendance
        fields = ['_id', 'date', 'teacher', 'today_present', 'reason']    

    def to_internal_value(self, data):
        if 'teacher' in data:
            data['teacher'] = ObjectId(data['teacher'])

        if 'today_present' in data:    
            data['today_present'] =  data["today_present"] == "True"
        
        if 'reason' in data:
            data['reason'] =  data.get("reason", "")
         
        return data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['teacher'] = str(instance.teacher._id)
        representation['today_present'] = str(instance.today_present)
        representation['reason'] = str(instance.reason)
        return representation
    
    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher')
        today_present = validated_data.pop('today_present')
        teacher = Teacher.objects.get(_id=teacher_id) 
        teacher_attendance = TeacherAttendance.objects.create(teacher=teacher, today_present=today_present, **validated_data)
        teacher_attendance.save()
        return teacher_attendance 
    
    def update(self, instance, validated_data):
        teacher_id = validated_data.get('teacher', instance.teacher)
        teacher = Teacher.objects.get(_id=ObjectId(teacher_id))
        instance.teacher = teacher
        instance.today_present = validated_data.get('today_present', instance.today_present) 
        instance.reason = validated_data.get('reason', instance.reason)

        instance.save()
        return instance
    
class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ['_id', 'school_class', 'subject', 'teacher', 'day_of_week', 'start_time', 'end_time']

    def to_internal_value(self, data):
        if 'school_class' in data :
            data['school_class'] = ObjectId(data['school_class'])

        if 'subject' in data:
            data['subject'] = ObjectId(data['subject'])

        if 'teacher' in data:
            data['teacher'] = ObjectId(data['teacher'])
          
        return data
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['teacher'] = str(instance.teacher._id)
        representation['subject'] = str(instance.subject._id)
        representation['school_class'] = str(instance.school_class._id)
        representation['day_of_week'] = str(instance.day_of_week)
        representation['start_time'] = str(instance.start_time)
        representation['end_time'] = str(instance.end_time)
        return representation
    
    def create(self, validated_data):
        teacher_id = validated_data.pop('teacher')
        subject_id = validated_data.pop('subject')
        school_class_id = validated_data.pop('school_class')
        day_of_week = validated_data.pop('day_of_week')
        start_time = validated_data.pop('start_time')
        end_time = validated_data.pop('end_time')

        teacher = Teacher.objects.get(_id=teacher_id)
        subject = Subject.objects.get(_id=subject_id)
        school_class = SchoolClass.objects.get(_id=school_class_id)

        timetable = Timetable.objects.create(
            school_class=school_class, 
            subject=subject, 
            teacher=teacher, 
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            )

        timetable.save() 

        return timetable
    
    def update(self, instance, validated_data):
        teacher_id = validated_data.get('teacher', instance.teacher)
        subject_id = validated_data.get('subject', instance.subject)
        school_class_id = validated_data.get('school_class', instance.school_class)
        
        teacher = Teacher.objects.get(_id=teacher_id)
        subject = Subject.objects.get(_id=subject_id)
        school_class = SchoolClass.objects.get(_id=school_class_id)

        instance.teacher = teacher
        instance.subject = subject
        instance.school_class = school_class
        instance.day_of_week = validated_data.get('day_of_week', instance.day_of_week)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        
        instance.save()
        return instance
    
class Examserializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['_id', 'exam_name', 'standard', 'created_by', 'attendance', 'total_mark', 'exam_date', 'subjects', 'start_time', 'end_time']

    def to_internal_value(self, data):
        if 'standard' in data:
            data['standard'] = ObjectId(data['standard'])
         
        if 'created_by' in data:
            data['created_by'] = ObjectId(data['created_by']) 

        if 'attendance' in data:
            data['attendance']  = ObjectId(data['attendance'])   

        if 'subjects' in data:
            data['subjects'] = [ ObjectId(subject_id) for subject_id in data['subjects']]

        return data        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['created_by'] = str(instance.created_by._id)
        representation['subjects'] = [ str(sub) for sub in instance.subjects]
        representation['exam_date'] = str(instance.exam_date)
        representation['exam_name'] = str(instance.exam_name)
        representation['standard'] = str(instance.standard._id)
        representation['attendance'] = str(instance.attendance._id)
        representation['total_mark'] = str(instance.total_mark)
        representation['start_time'] = str(instance.start_time)
        representation['end_time'] = str(instance.end_time)
        return representation 

    def create(self, validated_data):
        standard_id =  validated_data.pop('standard')
        created_id  =  validated_data.pop('created_by')
        attendance_id = validated_data.pop('attendance')

        standard = Standard.objects.get(_id=standard_id)
        created_by = User.objects.get(_id=created_id)
        attendance = Attendance.objects.get(_id=attendance_id)

        exam = Exam.objects.create(standard=standard, created_by=created_by, attendance=attendance, **validated_data)
         
        exam.save() 
        return exam   
    
    def update(self, instance, validated_data):
        instance.exam_name  = validated_data.get('exam_name', instance.exam_name)
        instance.exam_date = validated_data.get('exam_date', instance.exam_date)
        instance.total_mark = validated_data.get('total_mark', instance.total_mark)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)

        standard_id = validated_data.get('standard', instance.standard)
        created_id = validated_data.get('created_by', instance.created_by)
        attendance_id = validated_data.get('attendance', instance.attendance)

        standard = Standard.objects.get(_id=ObjectId(standard_id))
        attendance = Attendance.objects.get(_id=ObjectId(attendance_id))
       
        instance.standard = standard
        instance.created_by = User.objects.get(_id=ObjectId(created_id))
        instance.attendance = attendance  
        instance.subjects =  validated_data.get('subjects', instance.subjects)
        
        instance.save()
        return instance
    
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['_id', 'exam', 'student', 'marks_obtained', 'total_marks', 'percentage', 'grade', 'created_at']
    
    def to_internal_value(self, data):
        data['exam'] = ObjectId(data['exam'])
        data['student'] = ObjectId(data['student'])
         
        total_marks = 0
        save_data = []
        
        for markes_data in data['marks_obtained']:
            total_marks += int(markes_data['marks'])
            save_data.append({
            'subject' : ObjectId(markes_data['subject']),
            'marks' : int(markes_data['marks']),
            })
    
        data['marks_obtained'] = save_data
        data['total_marks'] = total_marks
        return data 
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['_id'] = str(instance._id)
        representation['exam'] = str(instance.exam._id)
        representation['student'] = str(instance.student._id)
        representation['total_marks'] = str(instance.total_marks)
        representation['percentage'] = str(instance.percentage)
        representation['grade'] = str(instance.grade)
        representation['created_at'] = str(instance.created_at)
        
        representation['marks_obtained'] = [{
            'subject':str(datas['subject']),
            'marks':str(datas['marks'])
        } for datas in instance.marks_obtained]
            

        return representation 

    def create(self, validated_data):
        exam_id = validated_data.pop('exam')
        student_id = validated_data.pop('student')
        total_mark =  validated_data.pop('total_marks')

        exam = Exam.objects.get(_id=exam_id)
        student = Student.objects.get(_id=student_id)
        
        total_possible_marks = exam.total_mark * len(exam.subjects)
        percentage =  (total_mark * 100 ) / total_possible_marks

        grade = calculate_grade(percentage)                       

        result = Result.objects.create(
            exam=exam, 
            student=student, 
            percentage=percentage,
            total_marks=total_mark, 
            grade=grade,
            **validated_data
        )
        
        result.save()
        return result
    
    def update(self, instance, validated_data):
        exam_id = validated_data.get('exam', instance.exam)
        student_id = validated_data.get('student', instance.student)
        total_mark =  validated_data.get('total_marks', instance.total_marks)

        exam = Exam.objects.get(_id=exam_id)
        student = Student.objects.get(_id=student_id)
        
        total_possible_marks = exam.total_mark * len(exam.subjects)
        percentage =  (total_mark * 100 ) / total_possible_marks

        grade = calculate_grade(percentage)  
 
        instance.exam = exam
        instance.student = student
        instance.grade = grade
        instance.total_marks = total_mark
        instance.percentage = percentage
        instance.marks_obtained = validated_data.get('marks_obtained', instance.marks_obtained)

        instance.save()
        return instance