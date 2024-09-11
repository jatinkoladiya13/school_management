from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from app.serializers import UserSerializer, VerifyOTPSerializer, ChangePasswordSerializer, RolleSerializer, PermissionSerializer, StanderSerializer, SubjectSerializer, SchoolClassSerializer, StudentSerializer, TeacherSerializer, AttendanceEnterySerializer, TeacherAttendanceSerializer, TeacherAttendance, TimetableSerializer, Examserializer, ResultSerializer 
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView, Response
from app.models import User, Rolle, Permission, Standard, Subject, SchoolClass, Student, Teacher, Attendance, Timetable, Exam, Result
from rest_framework.mixins import ListModelMixin, CreateModelMixin,  UpdateModelMixin, DestroyModelMixin
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from app.permission import Custompermission, CustomPermissionAdmin
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import Token
from djongo.models.fields import ObjectIdField
from rest_framework import status
from rest_framework import viewsets
from django.db.utils import IntegrityError
from app.customauthentication import CustomJWTAuthentication
import pymongo.errors
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from bson import ObjectId
from app.service import create_user, get_all_users, commen_init
import jwt
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from app.email import send_otp_via_email
from rest_framework.exceptions import ValidationError
from djongo.database import DatabaseError
from datetime import datetime, timedelta
from datetime import time 
from app.common_function import convert_object_id
from app.result_pdf import create_result_pdf
import pytz
# Create your views here.



def get_tookens_for_users(user):
    refreshtoken = RefreshToken()
    refreshtoken['user_id'] = str(user._id)
    return {
        'refresh':str(refreshtoken),
        'access': str(refreshtoken.access_token),
    }

def decode_access_token(access_token):
    try:
        decoded_token = jwt.decode(access_token, options={'verify_exp': False})  # Decode without verifying expiration
        return decoded_token
    except jwt.ExpiredSignatureError:
        return Response({'status':'404', 'msg':'Enter valit data'}, status=status.HTTP_404_NOT_FOUND)
    except jwt.InvalidTokenError:
        return Response({'status':'404', 'msg':'Enter valit data'}, status=status.HTTP_404_NOT_FOUND)
    
# @authentication_classes([BasicAuthentication])
# @permission_classes([AllowAny])
@csrf_exempt
@api_view(['POST'])
def usercreate(request):
   
    if request.method == 'POST':
        email=request.data.get('email')
        username = request.data.get('username')
        rolle = request.data.get('rolle')

        user = User.objects.filter(email=email).count() > 0 or  User.objects.filter(username=username).count() > 0 
        
        if user:
            return Response({'error': 'Email and Username address already exists.'}, status=status.HTTP_400_BAD_REQUEST)   

        
        if rolle == 'admin' and User.objects.filter(rolle='admin').count() > 0 :
            return Response({'error': 'There can only be one admin in the application.'}, status=status.HTTP_400_BAD_REQUEST)
       
        serializer = UserSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            res ={'status':'200', 'message':'successfully register..!'}
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type = "application/json")    
    return JsonResponse({'status':'400', 'message':'netwoor error'}, status=400) 

@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def userget(request):
    if request.method == 'GET':
        user = request.user
       
        serializer = UserSerializer(user)
        if user:
            res ={'status':'200', 'message':serializer.data}
            json_data = JSONRenderer().render(res)
            return HttpResponse(json_data, content_type = "application/json")    
    return JsonResponse({'status':'400', 'message':'netwoor error'}, status=400) 

class UserLoginView(APIView):


    def post(self, request, formate=None):
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(email=email).count() > 0  
        
        if user:    
            if email is not None and password is not None:
                user =authenticate(request, email=email, password=password)
                if user is not None:
                    try:
                        tokenso = OutstandingToken.objects.get(user_id=str(user._id))
                        if tokenso:
                            tokenB = BlacklistedToken.objects.get(token_id=tokenso.id)
                            tokenso.delete()
                            tokenB.delete()
                    except ObjectDoesNotExist:
                        pass

                if user is not None:
                    token = get_tookens_for_users(user)
                    return Response({'status':'200','token':token, 'msg':'login successfully..1'}, status=status.HTTP_200_OK)
                return Response({'status':'404', 'msg':'Enter 1 valit data'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'status':'404', 'msg':'Enter valit data'}, status=status.HTTP_404_NOT_FOUND)
    

class UserPutOrDeletView(APIView):
     
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated] 

    def put(self, request, formate=None):
        user = request.user
        
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'successfully update user'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, formate=None):
        user_id = request.user._id 
        user = User.objects.get(_id=ObjectId(user_id))
        user.delete()
        return Response({'status':'200', 'msg':'user delete successfully.....!'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def userlogout(request):
    if request.method == 'POST':
        refresh_token = request.data.get('refresh_token', '')
        try:
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            user_id = token.payload['user_id']
            outstanding = OutstandingToken.objects.get(token=refresh_token)
            outstanding.user_id = user_id
            outstanding.save()   
            
            return Response({"success": "User logged out successfully."}, status=status.HTTP_200_OK)
        except InvalidToken:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])        
def send_otp_view(request):
    if request.method == 'POST':
        try:
            email=request.data.get('email')
            user = User.objects.get(email=email)
            if user:
                send_otp_via_email(email)
                return  JsonResponse({'status':'200', 'msg':'successfully send otp in email.....!'}, status=200)
        except User.DoesNotExist:
            return  JsonResponse({'status':'404', 'msg':'user not found.....!'}, status=404)

class VerifyOTP(APIView):

    def post(self, request, ):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():

            email = serializer.data['email']
            otp = serializer.data['otp']

            try: 
                user = User.objects.get(email=email)
                if not user.otp ==  otp:
                    return  Response({'status':'404', 'msg':'Invalid otp.....!'}, status=status.HTTP_404_NOT_FOUND)
                if user.otp == otp:
                    user.otp = 1
                    user.save()
                    return  Response({'status':'200', 'msg':'successfully send otp verifyed.....!'}, status=status.HTTP_200_OK)
                return  Response({'status':'400', 'msg':'user  bad request.....!'}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return  Response({'status':'404', 'msg':'user not found.....!'}, status=status.HTTP_404_NOT_FOUND) 


class ChangePassword(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.data['email']
            password = serializer.data['password']

            user = User.objects.get(email=email)
            if user.otp == 1:
                user.otp = 0
                user.set_password(password)
                user.save()
                return  Response({'status':'200', 'msg':'successfully password change.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'Unverifeyed user.....!'}, status=status.HTTP_400_BAD_REQUEST)
    
class LCRollView(GenericAPIView,  ListModelMixin, CreateModelMixin):
    queryset = Rolle.objects.all()
    serializer_class = RolleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        rolle = request.data.get('rolle_name')
        if Rolle.objects.filter(rolle_name=rolle).count() > 0:
            return Response({'error': 'This Rolle already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        return self.create(request, request, *args, **kwargs)
    

class UDRolleview(APIView):

    def get(self, request, pk, *args, **kwargs):
       rolle_instance = Rolle.objects.get(_id=ObjectId(pk))
       if not rolle_instance:
           return Response({"detail": "Rolle not found."}, status=status.HTTP_404_NOT_FOUND)
       return Response({"status": "200", "msg": rolle_instance.rolle_name})

        
    def put(self, request, pk, *args, **kwargs): 
        roll =  Rolle.objects.get(_id=ObjectId(pk))

        serializer = RolleSerializer(roll, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'successfully update roll'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, *args, **kwargs):
        rolle =  Rolle.objects.get(_id=ObjectId(pk))
        rolle.delete()
        return Response({'msg':'successfully Delete'}, status=status.HTTP_204_NO_CONTENT)  


class PermissionCreateView(ListCreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    lookup_field = '_id'
    
    def perform_create(self, serializer):
        create = serializer.validated_data.get('create')
        update = serializer.validated_data.get('update')
        delete_permission = serializer.validated_data.get('delete_permission')
        view = serializer.validated_data.get('view')

        if Permission.objects.filter(create=create, update=update, delete_permission=delete_permission, view=view).count() > 0:
            raise ValidationError({'error': 'This permission already exists.'})
        serializer.save()


class PermissionUpdateordeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer 
    lookup_field = '_id'

    def get_object(self):
        try:
            object_id = self.kwargs.get(self.lookup_field)
            return Permission.objects.get(_id=ObjectId(object_id))
        except Permission.DoesNotExist:
            raise      

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({"detail": "Permission not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)      
        return Response({"detail": "Permission deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class StanderAllView(viewsets.ViewSet):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated, Custompermission]

    
    def create(self, request): 
        student_stander = request.data.get('student_stander')
        
        check = Standard.objects.filter(student_stander=student_stander).count() > 0
        if check:
            return  Response({'status':'404', 'msg':'already this data saved.....!'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StanderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response({'status':'200', 'msg':'Stander create successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        standard = Standard.objects.all()
        serializer = StanderSerializer(standard, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)
    
    def update(self, request, pk):
        starnder = Standard.objects.get(_id= ObjectId(pk))
        serializer = StanderSerializer(starnder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Stander update successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk,):
        standar = Standard.objects.get(_id=ObjectId(pk))
        standar.delete()
        return Response({'status':'200', 'msg':'Stander delete successfully.....!'}, status=status.HTTP_200_OK) 


class SubjectAllview(viewsets.ViewSet):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated, Custompermission]  


    def create(self, request):
        subject  = request.data.get('subject')

        check  = Subject.objects.filter(subject=subject).count() > 0
        if check:
                    return  Response({'status':'404', 'msg':'already this data saved.....!'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Stander Subject successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        subject = Subject.objects.all()
        serializer = SubjectSerializer(subject, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)
    
    def update(self, request, pk):
        print("this is working or not")
        subject = Subject.objects.get(_id=ObjectId(pk))
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Subject update successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subject = Subject.objects.get(_id=ObjectId(pk))
        subject.delete()
        return Response({'status':'200', 'msg':'Subject delete successfully.....!'}, status=status.HTTP_200_OK) 


class SchoolClassView(APIView):

    def post(self, request, *args, **kwargs):
        class_name = request.data.get('class_name')
        clas = SchoolClass.objects.filter(class_name=class_name).count() > 0
        if clas: 
            return  Response({'status':'404', 'msg':'already this data saved.....!'}, status=status.HTTP_404_NOT_FOUND)
          
        serializer = SchoolClassSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'School Class Create successfully.....!'}, status=status.HTTP_200_OK)  

    def get(self, request, *args, **kwargs):
        class_name = SchoolClass.objects.all()
        serializer = SchoolClassSerializer(class_name, many=True)
        return Response({'status':'200', 'msg': serializer.data}, status=status.HTTP_200_OK) 

class SchoolUDView(APIView):

    def put(self, request, pk, *args, **kwargs):
        school_class = SchoolClass.objects.get(_id=ObjectId(pk))
        serializer = SchoolClassSerializer(school_class, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'School update successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        school_class = SchoolClass.objects.get(_id=ObjectId(pk))
        school_class.delete()
        return Response({'status':'200', 'msg':'School Class Delete successfully.....!'}, status=status.HTTP_200_OK)  


class StudentAllView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated, Custompermission] 

    def post(self, request, *args, **kwargs):
        user = request.data.get('user')
        school_class = request.data.get('school_class')                                    
        roll_number = request.data.get('roll_number')
        
        check = Student.objects.filter(user=ObjectId(user)).count() >0
        if check:
            return  Response({'status':'404', 'msg':'already this data saved.....!'}, status=status.HTTP_404_NOT_FOUND)
    
        roll_number_check = Student.objects.filter(school_class=ObjectId(school_class), roll_number=roll_number).count() > 0
        if roll_number_check:
            return Response({'status': '404', 'msg': 'This roll number already exists in the specified class.'}, status=status.HTTP_404_NOT_FOUND)

        
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'status':'200', 'msg':'Student Create successfully.....!'}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return  Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)

    def  get(self, request, *args, **kwargs):
        student = Student.objects.all()
        serializer  = StudentSerializer(student, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)
    
class StudentUDView(APIView):

    def put(self, request, pk, *args, **kwargs):
        school_class = request.data.get('school_class')                                    
        roll_number = request.data.get('roll_number')
        
        student = Student.objects.get(_id=ObjectId(pk))
        
        roll_number_check = Student.objects.filter(school_class=ObjectId(school_class), roll_number=roll_number).count() > 0
        if roll_number_check:
            return Response({'status': '404', 'msg': 'This roll number already exists in the specified class.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'status':'200', 'msg':'Student Update successfully.....!'}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status':'400', 'msg':'some  Issues.....!'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        student  = Student.objects.get(_id=ObjectId(pk))
        student.delete()
        return Response({'status':'200', 'msg':'Subject delete successfully.....!'}, status=status.HTTP_200_OK)


class TeacherView(APIView):

    def post(self, request, *args, **kwargs):
        user = request.data.get('user')
        qualification = request.data.get('qualification')
        check = Teacher.objects.filter(user=User.objects.get(_id=ObjectId(user)), qualification=qualification).count() > 0
        if check:
            return  Response({'status':'404', 'msg':'already this data saved.....!'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            try: 
                serializer.save()
                return Response({'status':'200', 'msg':'Teacher Create successfully.....!'}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return  Response({'status':'400', 'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        teacher = Teacher.objects.all()
        serializer = TeacherSerializer(teacher, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)
    

class TeacherUDview(APIView):

    def put(self, request, pk, *args, **kwargs):
        teacher = Teacher.objects.get(_id=ObjectId(pk))
        serializer = TeacherSerializer(teacher, data= request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Teacher Update successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        teacher = Teacher.objects.get(_id=ObjectId(pk))
        teacher.delete()
        return Response({'status':'200', 'msg':'Teacher Delete successfully.....!'}, status=status.HTTP_200_OK)
    
class AttendanceVeiw(APIView):

    def post(self, request, *args, **kwargs):
        teacher_id = request.data.get('teacher')
        
        # attendance = Attendance.objects.filter(teacher=ObjectId(teacher_id)).count() > 0
        # if attendance:
        #     return Response({'status':'200', 'msg':'Teacher  successfully.....!'}, status=status.HTTP_200_OK)

        serializer = AttendanceEnterySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Attendance create by teacher  successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

    def get(self, request, *args, **kwargs):
        attendance = Attendance.objects.all()
        serializer = AttendanceEnterySerializer(attendance, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)

class AttendanceUDVeiw(APIView):

    def put(self, request, pk, *args, **kwargs):
        attendance = Attendance.objects.get(_id=ObjectId(pk))

        serializer = AttendanceEnterySerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'200', 'msg':'Attendance Update by teacher  successfully.....!'}, status=status.HTTP_200_OK)
        return  Response({'status':'400', 'msg':serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

    def delete(self, request, pk, *args, **kwargs):
        attendance = Attendance.objects.get(_id=ObjectId(pk))
        attendance.delete()
        return Response({'status':'200', 'msg':'Attendance Delete by teacher  successfully.....!'}, status=status.HTTP_200_OK)

class menullyUpdateview(APIView):

    def put(self, request, pk, *args, **kwargs):
        student = request.data.get('student')
        today_present = request.data.get('today_present')
        reason = request.data.get('reason')

        attendance_data  =  Attendance.objects.get(_id=ObjectId(pk))
          
        for attendance in attendance_data.attendance:
            if str(attendance['student']) == student:
                to_present = today_present == "True"
                attendance['today_present'] = to_present
                attendance['reason'] = reason
                break
        
        attendance_data.save() 
        return Response({'status':"200", 'msg': "this is working and good fore me"}, status=status.HTTP_200_OK)


class AttendanceAggregationPipelineView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            sta_date = request.data.get('start_date')
            en_date = request.data.get('end_date')
            teacher_id = request.data.get('teacher_id') 
            present = request.data.get('present')
            
            users_collection = commen_init('app_attendance')
            start_date = datetime.strptime(sta_date, '%Y-%m-%d')
            end = datetime.strptime(en_date, '%Y-%m-%d')
            end_date = end + timedelta(days=1)

            pipeline = [
                {
                    "$unwind": "$attendance"
                }, 
            ]
            
            match_stage = {
                "teacher_id": ObjectId(teacher_id),
                "date": {"$gte": start_date, "$lt": end_date}
            }

            if present is not None:
                match_stage["attendance.today_present"] = present == 'True'
         
            pipeline.append({
                "$match": match_stage
            })

            pipeline.extend([
                {
                    "$group": {
                        "_id": {
                            "teacher": "$teacher_id",
                            "date": "$date",
                            "_id": "$_id"
                        },
                        "presentStudents": {
                            "$push": {
                                "student": "$attendance.student",
                                "today_present": "$attendance.today_present"
                            }
                        },
                        "attendanceCount": {"$sum": 1}
                    }
                },
            ])
            attendance = list(users_collection.aggregate(pipeline))
            attendance = convert_object_id(attendance)
            return Response(attendance)
        except DatabaseError as e:
            return Response({"error": str(e)}, status=500) 
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    

class TeacherAttendanceView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated, CustomPermissionAdmin] 
    def post(self, request, *args, **kwargs):
        teacher = request.data.get('teacher')
        count =  TeacherAttendance.objects.filter(teacher=ObjectId(teacher), date = datetime.now()).count() > 0
        if count:
            return Response({"status":"400", "msg":"this data is already exists......!"})

        serializer = TeacherAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Teacher attendance successfully add............"}, status=status.HTTP_200_OK)
        return Response({"status":"400", "msg":serializer.errors})
    
    def get(self, request, *args, **kwargs):
        teacher_attendance = TeacherAttendance.objects.all()
        serializer = TeacherAttendanceSerializer(teacher_attendance, many=True)
        return Response({'status':"200", 'msg': serializer.data}, status=status.HTTP_200_OK)

class TeacherAttendanceUDview(APIView):
    # authentication_classes = [CustomJWTAuthentication]    
    # permission_classes = [IsAuthenticated, CustomPermissionAdmin] 
    def put(self, request, pk, *args, **kwargs):
        teacher_attendance = TeacherAttendance.objects.get(_id=ObjectId(pk))
        serializer = TeacherAttendanceSerializer(teacher_attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Teacher attendance successfully Update............"}, status=status.HTTP_200_OK)
        return Response({"status":"400", "msg":serializer.errors})
    
    def delete(self, request, pk, *args, **kwargs):
        teacher_attendance = TeacherAttendance.objects.get(_id=ObjectId(pk))
        teacher_attendance.delete()
        return Response({'status':"200", 'msg': "Teacher attendance successfully Delete............"}, status=status.HTTP_200_OK)


class TeacherAttendanceAggPipView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated, CustomPermissionAdmin] 
    def post(self, request, *args, **kwargs):
        try:
            users_collection = commen_init('app_teacherattendance')
            star_date = request.data.get('start_date')
            en_date = request.data.get('end_date')
            present = request.data.get('present')
            teacher_id = request.data.get('teacher_id')

          
            start_date = datetime.strptime(star_date, '%Y-%m-%d')
            end = datetime.strptime(en_date, '%Y-%m-%d')
            end_date = end + timedelta(days=1)

            pipeline = []
            
            match_stage = {
                "teacher_id": ObjectId(teacher_id),
               "date": {"$gte": start_date, "$lt": end_date}
            }

            if present is not None:
                match_stage["today_present"] = present == 'True'
         
            pipeline.append({
                "$match": match_stage
            })

            pipeline.extend([
                {
                    "$group": {
                        "_id": {
                            "teacher": "$teacher_id",
                            "date": "$date",
                            "_id": "$_id",
                            "today_present": "$today_present" 
                        },
                       
                    }
                },
            ])

            attendance = list(users_collection.aggregate(pipeline))
            attendance = convert_object_id(attendance)
            return Response(attendance) 
        
        except DatabaseError as e:
            return Response({"error": str(e)}, status=500) 
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class TimetableView(APIView):

    def post(self, request, *args, **kwargs):
        school_class_id = request.data.get('school_class')
        day_of_week = request.data.get('day_of_week')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        timetable_filter = Timetable.objects.filter(school_class=ObjectId(school_class_id), day_of_week=day_of_week, start_time=start_time, end_time=end_time).count() > 0
        if timetable_filter:    
            return Response({"status":"400", "msg":"this data is already exists......!"})
       
        serializer = TimetableSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Timetable create successfully............"}, status=status.HTTP_200_OK)
        return Response({"status":"400", "msg":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
        timetable = Timetable.objects.all()
        serializer = TimetableSerializer(timetable, many=True)
        return Response({'status':'200', 'msg':serializer.data}, status=status.HTTP_200_OK)
    
class TimetableUDView(APIView):

    def put(self, request, pk, *args, **kwargs):
        timetable = Timetable.objects.get(_id=ObjectId(pk)) 
        serializer = TimetableSerializer(timetable, data=request.data) 
        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Timetable Update successfully............"}, status=status.HTTP_200_OK)
        return  Response({'status':"400", 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk, *args, **kwargs):
        timetable  = Timetable.objects.get(_id=ObjectId(pk))
        timetable.delete()
        return Response({'status':"200", 'msg': "Timetable successfully Delete............"}, status=status.HTTP_200_OK)
    

class TimelectureAggPip(APIView):

    def post(self, request, *args, **kwargs):
        times = request.data.get('time', None)
        day  = request.data.get('day')
        
        timetable_data = []
        if times and day is not None:
            target_time = datetime.strptime(times, '%H:%M:%S').time() 
            timetable_data = Timetable.objects.filter(start_time__lte=target_time, end_time__gte=target_time, day_of_week=day)
        else:
            timetable_data = Timetable.objects.all()

        serializer = TimetableSerializer(timetable_data, many=True)    
        return Response({'status':"200", 'msg': serializer.data}, status=status.HTTP_200_OK)

class Examview(APIView):

    def post(self, request, *args, **kwargs):

        standard = request.data.get('standard')
        subjects_id = request.data.get('subjects')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        subjects = [ObjectId(id) for id in subjects_id] 
        exam_filter = Exam.objects.filter(start_time__lte= start_time, end_time__gte = end_time, subjects = subjects, standard=ObjectId(standard),).count() > 0
        if exam_filter:
            return Response({"status":"400", "msg":"this data is already exists......!"})

        serializer =  Examserializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Exam create successfully............"}, status=status.HTTP_200_OK)
        return  Response({'status':"400", 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        exam = Exam.objects.all()
        serializer = Examserializer(exam, many=True)
        return Response({'status':"200", 'msg': serializer.data}, status=status.HTTP_200_OK)
    

class ExamUDView(APIView):

    def put(self, request, pk, *args, **kwargs):

        exam = Exam.objects.get(_id=ObjectId(pk))
        serializer = Examserializer(exam, data=request.data)

        if serializer.is_valid():
            serializer.save()  
            return Response({'status':"200", 'msg': "Exam Update successfully............"}, status=status.HTTP_200_OK)
        return  Response({'status':"400", 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        exam = Exam.objects.get(_id=ObjectId(pk))
        exam.delete()
        return Response({'status':"200", 'msg': "Exam successfully Delete............"}, status=status.HTTP_200_OK)
    
class ResultView(APIView):

    def post(self, request, *args, **kwargs):
        exam_id = request.data.get('exam')
        student = request.data.get('student')
        marks_obtained = request.data.get('marks_obtained')

        if not exam_id or not student or not marks_obtained:
            return Response({"status": "400", "msg": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            exam = Exam.objects.get(_id=ObjectId(exam_id))
        except Exam.DoesNotExist:
            return Response({"status": "400", "msg": "Exam not found"}, status=status.HTTP_400_BAD_REQUEST)    

        subject_ids_list2 = {ObjectId(entry['subject']) for entry in marks_obtained}

        if not subject_ids_list2.issubset(exam.subjects):
            return Response({"status": "400", "msg": "Invalid subjects provided"}, status=status.HTTP_400_BAD_REQUEST)
    
        if   Result.objects.filter(exam = ObjectId(exam_id), student=ObjectId(student)).count() > 0 :
            return Response({"status": "400", "msg": "Result already exists for this student and exam"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':"200", 'msg': "Result create successfully............"}, status=status.HTTP_200_OK)
        return  Response({'status':"400", 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        result = Result.objects.all()
        serializer = ResultSerializer(result, many=True)
        return  Response({'status':"200", 'msg': serializer.data}, status=status.HTTP_200_OK)
    
class ResultUDView(APIView):

    def put(self, request, pk, *args, **kwargs):  
        result = Result.objects.get(_id=ObjectId(pk))
        serializer = ResultSerializer(result, data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response({'status':"200", 'msg': "Result Update successfully............"}, status=status.HTTP_200_OK)
        return  Response({'status':"400", 'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, *args, **kwargs):
        result = Result.objects.get(_id=ObjectId(pk))
        result.delete()
        return Response({'status':"200", 'msg': "Result successfully Delete............"}, status=status.HTTP_200_OK)
    

class Resultfilter(APIView):

    def post(self, request, *args, **kwargs):
        check_status = request.data.get('check_status')
        subject_name = request.data.get('subject')
        student_name = request.data.get('student_name')

        result_queryset = Result.objects.all()
        
        if check_status == 'Pass':
            result_queryset = result_queryset.filter(grade__in=['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D'])
            
        if subject_name:
            subject = get_object_or_404(Subject, subject=subject_name)
            subject_id = ObjectId(subject._id)

            sub_filter_data = []
            for res_data in result_queryset:
                for sub_data in res_data.marks_obtained:
                    if sub_data['subject']  == subject_id:
                        sub_filter_data.append({
                            '_id':str(res_data._id),
                            'exam_id': str(res_data.exam._id),
                            'exam_name': res_data.exam.exam_name,
                            'marks': sub_data['marks'],
                            'grade': res_data.grade,
                            'percentage': res_data.percentage
                        }) 
            
            result_queryset = Result.objects.filter(_id__in=[ObjectId(item['_id']) for item in sub_filter_data])

              
        if student_name:
            result_queryset = result_queryset.filter(student__user__username = student_name)
      
        serializer = ResultSerializer(result_queryset, many=True)
        return Response({'status':'200', 'data':serializer.data})
        



