from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("forgot-password/", ForgotPasswordAPIView.as_view()),
    path("verify-otp/", VerifyOTPAPIView.as_view()),
    path("reset-password/", ResetPasswordAPIView.as_view()),
    path("profile/", UserProfileAPIView.as_view()),

    path("departments/", DepartmentListAPIView.as_view(), name="department-list"),
    path("years/<int:department_id>/", YearListAPIView.as_view()),
    path("subjects/", SubjectListAPIView.as_view(), name="subjects"),
    path("subjects/detail/", SubjectDetailAPIView.as_view(), name="subject-detail"),
    path("notes/", NotesListAPIView.as_view(), name="notes"),
    path("notes/detail/", NotesDetailAPIView.as_view(), name="notes-detail"),
    path("notes/download/", DownloadNoteAPIView.as_view(), name="notes-download"),
    path("comments/", CommentAPIView.as_view(), name="comments"),
    path("ratings/", RatingAPIView.as_view(), name="ratings"),
    path("contact/", ContactCreateAPIView.as_view(), name="contact"),



    path("api/admin/dashboard/", AdminDashboardAPIView.as_view()),
    path("api/admin/users/", AdminUserListAPIView.as_view()),
    path("api/admin/departments/", AdminDepartmentListCreateAPIView.as_view()),
    path("api/admin/departments/<int:pk>/", AdminDepartmentDetailAPIView.as_view()),
    path("api/admin/years/", AdminYearListCreateAPIView.as_view()),
    path("api/admin/years/<int:pk>/", AdminYearDetailAPIView.as_view()),
    path("api/admin/subjects/", AdminSubjectListCreateAPIView.as_view()),
    path("api/admin/subjects/<int:pk>/", AdminSubjectDetailAPIView.as_view()),
    path("api/admin/notes/", AdminNotesListCreateAPIView.as_view()),
    path("api/admin/notes/<int:pk>/", AdminNotesDetailAPIView.as_view()),
    path("api/admin/contacts/", AdminContactListAPIView.as_view()),
    path("api/admin/contacts/<int:pk>/", AdminContactDetailAPIView.as_view()),

    path("api/admin/login/", AdminLoginAPIView.as_view()),

]