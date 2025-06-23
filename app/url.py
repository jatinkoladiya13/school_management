
from django.urls import path, include
from app import views
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('stander', views.StanderAllView, basename="stander")
router.register('subject', views.SubjectAllview, basename="subject")


urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh_view'),
    path('usercreate/',views.usercreate, name="usercreate"),
    path('userget/',views.userget, name="userget"),
    path('userlogin/', views.UserLoginView.as_view(), name="userlogin"),
    path('userputordeleteview/', views.UserPutOrDeletView.as_view(), name='userputordeleteview'),
    path('userlogout/', views.userlogout, ),
    path('sendotp/', views.send_otp_view),
    path('verifyotp/',views.VerifyOTP.as_view()),
    path('changepassword/', views.ChangePassword.as_view()),
    path('creatorgetroll/', views.LCRollView.as_view()),
    path('udrolleview/<str:pk>/', views.UDRolleview.as_view()),
    path('permissioncreateview/', views.PermissionCreateView.as_view(), name='permissioncreateview'), 
    path('retriveUpdateDeleteRolle/<str:_id>/', views.PermissionUpdateordeleteView.as_view()), 
    path('standerorsubjectview/', include(router.urls), ),
    path('studentview/', views.StudentAllView.as_view()),
    path('studeudview/<str:pk>/', views.StudentUDView.as_view()),
    path('teacherview/', views.TeacherView.as_view()),
    path('teacherUDview/<str:pk>/', views.TeacherUDview.as_view()),
    path('schoolclassview/', views.SchoolClassView.as_view()),
    path('schoolUDview/<str:pk>/', views.SchoolUDView.as_view()),
    path('attendanceveiw/', views.AttendanceVeiw.as_view()),
    path('attendanceudveiw/<str:pk>/', views.AttendanceUDVeiw.as_view()),
    path('attendancemenullyupdate/<str:pk>/', views.menullyUpdateview.as_view()),
    path('AttendanceAggregationPipelineView/', views.AttendanceAggregationPipelineView.as_view()),
    path('teacherattendance/', views.TeacherAttendanceView.as_view()),
    path('teacherattendanceUD/<str:pk>/', views.TeacherAttendanceUDview.as_view()),
    path('teacherattendanceAggPip/', views.TeacherAttendanceAggPipView.as_view()),
    path('timetableview/', views.TimetableView.as_view()),
    path('timetableUDview/<str:pk>/', views.TimetableUDView.as_view()),
    path('timelectureAggPip/', views.TimelectureAggPip.as_view()),
    path('examview/', views.Examview.as_view()),
    path('examUDView/<str:pk>/', views.ExamUDView.as_view()),
    path('resultview/',views.ResultView.as_view()),
    path('resultUDView/<str:pk>/',views.ResultUDView.as_view()),
    path('resultfilter/', views.Resultfilter.as_view()),

]

