from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsUser, IsAdmin
from django.http import FileResponse, Http404
from .utils import *
from django.http import FileResponse, Http404
import os
import random
from django.core.mail import send_mail
from django.conf import settings



from rest_framework.generics import (
    GenericAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)



# class RegisterAPIView(GenericAPIView):
#     serializer_class = RegisterSerializer

#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"status": True,"message": "User Registered Successfully","data": serializer.data},status=status.HTTP_201_CREATED)
#         return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)



class SendRegistrationOTPAPIView(GenericAPIView):
    serializer_class = SendRegistrationOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "status": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        email = data["email"]

        # Check email already registered
        if UserRegister.objects.filter(email=email).exists():
            return Response(
                {
                    "status": False,
                    "message": "Email already registered."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Delete previous OTP if exists
        RegistrationOTP.objects.filter(email=email).delete()

        otp = str(random.randint(100000, 999999))

        RegistrationOTP.objects.create(
            full_name=data["full_name"],
            username=data["username"],
            phone_number=data["phone_number"],
            email=email,
            password=data["password"],      # save hashed password in serializer
            otp=otp
        )

        try:
            send_mail(
                subject="Notes Arena Registration OTP",
                message=f"""
Hello {data['full_name']},

Your Registration OTP is:

{otp}

This OTP is valid for 5 minutes.

Regards,
Notes Arena Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        except Exception as e:
            # Clean up the OTP object since we couldn't send the email
            RegistrationOTP.objects.filter(email=email).delete()
            return Response(
                {
                    "status": False,
                    "message": "Failed to send OTP email. Please check backend email configuration.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "status": True,
                "message": "OTP sent successfully."
            },
            status=status.HTTP_200_OK
        )



class VerifyRegistrationOTPAPIView(GenericAPIView):
    serializer_class = VerifyRegistrationOTPSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            otp_obj = RegistrationOTP.objects.get(email=email)

        except RegistrationOTP.DoesNotExist:

            return Response(
                {
                    "status": False,
                    "message": "OTP not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if otp_obj.is_expired():
            otp_obj.delete()

            return Response(
                {
                    "status": False,
                    "message": "OTP expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.otp != otp:

            return Response(
                {
                    "status": False,
                    "message": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj.is_verified = True
        otp_obj.save()

        return Response(
            {
                "status": True,
                "message": "OTP verified successfully."
            },
            status=status.HTTP_200_OK
        )


class CompleteRegistrationAPIView(GenericAPIView):

    serializer_class = CompleteRegistrationSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]

        try:
            otp_obj = RegistrationOTP.objects.get(email=email)

        except RegistrationOTP.DoesNotExist:

            return Response(
                {
                    "status": False,
                    "message": "Registration request not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if otp_obj.is_expired():

            otp_obj.delete()

            return Response(
                {
                    "status": False,
                    "message": "OTP expired."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not otp_obj.is_verified:

            return Response(
                {
                    "status": False,
                    "message": "Please verify OTP first."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = UserRegister.objects.create_user(
            full_name=otp_obj.full_name,
            username=otp_obj.username,
            phone_number=otp_obj.phone_number,
            email=otp_obj.email,
            password=otp_obj.password
        )

        otp_obj.delete()

        return Response(
            {
                "status": True,
                "message": "Registration completed successfully.",
                "data": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "username": user.username,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED
        )


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": True,
                    "message": "Login Successful",
                    "data": {"id": user.id,"full_name": user.full_name,"username": user.username,"email": user.email,},
                    "tokens": {"access": str(refresh.access_token),"refresh": str(refresh),}
                },status=status.HTTP_200_OK)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)



class ForgotPasswordAPIView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        user = UserRegister.objects.get(email=email)
        # Delete previous OTPs
        OTPVerification.objects.filter(user=user).delete()
        otp = str(random.randint(100000, 999999))
        OTPVerification.objects.create(
            user=user,
            otp=otp
        )
        try:
            send_mail(
                subject="Notes Arena Password Reset OTP",
                message=f"""
Hello {user.full_name},

Your OTP for password reset is:

{otp}

This OTP is valid for 5 minutes.

Do not share this OTP with anyone.

Regards,
Notes Arena Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception as e:
            OTPVerification.objects.filter(user=user).delete()
            return Response(
                {
                    "message": "Failed to send OTP email. Please check backend email configuration.",
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "OTP sent successfully."
            },
            status=status.HTTP_200_OK,
        )




    
class VerifyOTPAPIView(GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        try:
            user = UserRegister.objects.get(email=email)
        except UserRegister.DoesNotExist:
            return Response(
                {
                    "error": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            otp_obj = OTPVerification.objects.filter(user=user).latest("created_at")
        except OTPVerification.DoesNotExist:
            return Response(
                {
                    "error": "OTP not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        if otp_obj.is_expired():
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp_obj.otp != otp:
            return Response(
                {
                    "error": "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp_obj.is_verified = True
        otp_obj.save()
        return Response(
            {
                "message": "OTP verified successfully."
            },
            status=status.HTTP_200_OK,
        )





class ResetPasswordAPIView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]
        try:
            user = UserRegister.objects.get(email=email)
        except UserRegister.DoesNotExist:
            return Response(
                {
                    "error": "User not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            otp_obj = OTPVerification.objects.filter(user=user).latest("created_at")
        except OTPVerification.DoesNotExist:
            return Response(
                {
                    "error": "Please verify OTP first."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp_obj.is_expired():
            otp_obj.delete()
            return Response(
                {
                    "error": "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not otp_obj.is_verified:
            return Response(
                {
                    "error": "OTP is not verified."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        otp_obj.delete()
        return Response(
            {
                "message": "Password reset successfully."
            },
            status=status.HTTP_200_OK,
        )





class UserProfileAPIView(GenericAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsUser]

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response({"status": True,"data": serializer.data},status=status.HTTP_200_OK)




class DepartmentListAPIView(GenericAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsUser]
    def get(self, request):
        departments = Department.objects.all()
        serializer = self.get_serializer(departments, many=True)
        return Response({"status": True,"count": departments.count(),"data": serializer.data},status=status.HTTP_200_OK)




class YearListAPIView(GenericAPIView):
    serializer_class = YearSerializer
    permission_classes = [IsUser]

    def get(self, request, department_id):
        years = Year.objects.filter(department_id=department_id)
        serializer = self.get_serializer(years, many=True)
        return Response({"status": True,"count": years.count(),"data": serializer.data},status=status.HTTP_200_OK)




class SubjectListAPIView(GenericAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsUser]

    def get(self, request):
        department_id = request.GET.get("department_id")
        year_id = request.GET.get("year_id")
        if not department_id or not year_id:
            return Response({"status": False,"message": "department_id and year_id are required."},status=status.HTTP_400_BAD_REQUEST)
        subjects = Subject.objects.filter(department_id=department_id,year_id=year_id)
        serializer = self.get_serializer(subjects, many=True)
        return Response({"status": True,"count": subjects.count(),"data": serializer.data},status=status.HTTP_200_OK)




class SubjectDetailAPIView(GenericAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [IsUser]

    def get(self, request):
        subject_id = request.GET.get("subject_id")
        if not subject_id:
            return Response({"status": False,"message": "subject_id is required."},status=status.HTTP_400_BAD_REQUEST)
        subject = Subject.objects.filter(id=subject_id).first()
        if not subject:
            return Response({"status": False,"message": "Subject not found."},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(subject)
        return Response({"status": True,"data": serializer.data},status=status.HTTP_200_OK)




class NotesListAPIView(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = [IsUser]

    def get(self, request):
        subject_id = request.GET.get("subject_id")
        if not subject_id:
            return Response({"status": False,"message": "subject_id is required."},status=status.HTTP_400_BAD_REQUEST)
        notes = Notes.objects.filter(subject_id=subject_id)
        serializer = self.get_serializer(notes, many=True)
        return Response({"status": True,"count": notes.count(),"data": serializer.data},status=status.HTTP_200_OK)




class NotesDetailAPIView(GenericAPIView):
    serializer_class = NotesSerializer
    permission_classes = [IsUser]

    def get(self, request):
        note_id = request.GET.get("note_id")
        if not note_id:
            return Response({"status": False,"message": "note_id is required."},status=status.HTTP_400_BAD_REQUEST)
        note = Notes.objects.filter(id=note_id).first()
        if not note:
            return Response({"status": False,"message": "Note not found."},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(note)
        return Response({"status": True,"data": serializer.data},status=status.HTTP_200_OK)




# class DownloadNoteAPIView(GenericAPIView):
#     permission_classes = [IsUser]

#     def get(self, request):
#         note_id = request.GET.get("note_id")
#         if not note_id:
#             return Response({"status": False,"message": "note_id is required."},status=status.HTTP_400_BAD_REQUEST)
#         note = Notes.objects.filter(id=note_id).first()
#         if not note or not note.file:
#             return Response({"status": False,"message": "Note not found."},status=status.HTTP_404_NOT_FOUND)
#         try:
#             return FileResponse(note.file.open("rb"),as_attachment=True,filename=note.file.name.split("/")[-1])
#         except FileNotFoundError:
#             raise Http404("File not found.")


class DownloadNoteAPIView(GenericAPIView):
    permission_classes = [IsUser]

    def get(self, request):
        note_id = request.GET.get("note_id")
        if not note_id:
            return Response({"status": False,"message": "note_id is required."},status=status.HTTP_400_BAD_REQUEST)
        try:
            note = Notes.objects.get(id=note_id)
        except Notes.DoesNotExist:
            return Response({"status": False,"message": "Note not found."},status=status.HTTP_404_NOT_FOUND)
        if not note.file:
            raise Http404("File not found.")
        # Increase download count
        note.downloads += 1
        note.save(update_fields=["downloads"])
        return FileResponse(
            note.file.open("rb"),
            as_attachment=True,
            filename=os.path.basename(note.file.name),
            content_type="application/pdf",)



class CommentAPIView(GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsUser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"status": True,"message": "Comment added successfully","data": serializer.data},status=status.HTTP_201_CREATED)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        comment_id = request.data.get("comment_id")
        comment = Comments.objects.filter(id=comment_id, user=request.user).first()
        if not comment:
            return Response({"status": False,"message": "Comment not found."},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True,"message": "Comment updated successfully","data": serializer.data},status=status.HTTP_200_OK)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        comment_id = request.data.get("comment_id")
        comment = Comments.objects.filter(id=comment_id, user=request.user).first()
        if not comment:
            return Response({"status": False,"message": "Comment not found."},status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({"status": True,"message": "Comment deleted successfully"},status=status.HTTP_200_OK)




class RatingAPIView(GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsUser]

    def post(self, request):
        note_id = request.data.get("notes")
        existing = Rating.objects.filter(notes_id=note_id,user=request.user).first()
        if existing:
            return Response(
                {"status": False,"message": "You have already rated this note. Use update instead."},status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"status": True,"message": "Rating added successfully","data": serializer.data},status=status.HTTP_201_CREATED)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        rating_id = request.data.get("rating_id")
        rating = Rating.objects.filter(id=rating_id, user=request.user).first()
        if not rating:
            return Response({"status": False,"message": "Rating not found."},status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(rating, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True,"message": "Rating updated successfully","data": serializer.data},status=status.HTTP_200_OK)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        rating_id = request.data.get("rating_id")
        rating = Rating.objects.filter(id=rating_id, user=request.user).first()
        if not rating:
            return Response({"status": False,"message": "Rating not found."},status=status.HTTP_404_NOT_FOUND)
        rating.delete()
        return Response({"status": True,"message": "Rating deleted successfully"},status=status.HTTP_200_OK)




class ContactCreateAPIView(GenericAPIView):
    serializer_class = ContactSerializer
    permission_classes = [IsUser]
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                    "message": "Message sent successfully",
                    "data": serializer.data
                },status=status.HTTP_201_CREATED)
        return Response({"status": False,"errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST)













    
class AdminDepartmentListCreateAPIView(ListCreateAPIView):
    serializer_class = AdminDepartmentSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Department.objects.all()




class AdminDepartmentDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminDepartmentSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Department.objects.all()




class AdminYearListCreateAPIView(ListCreateAPIView):
    serializer_class = AdminYearSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]

    def get_queryset(self):
        department_id = self.request.GET.get("department_id")
        qs = Year.objects.all()
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs




class AdminYearDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminYearSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Year.objects.all()




class AdminSubjectListCreateAPIView(ListCreateAPIView):
    serializer_class = AdminSubjectSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = Subject.objects.all()
        department_id = self.request.GET.get("department_id")
        year_id = self.request.GET.get("year_id")
        if department_id:
            qs = qs.filter(department_id=department_id)
        if year_id:
            qs = qs.filter(year_id=year_id)
        return qs




class AdminSubjectDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminSubjectSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Subject.objects.all()




# class AdminNotesListCreateAPIView(ListCreateAPIView):
#     serializer_class = AdminNotesSerializer
#     authentication_classes = []
#     permission_classes = [IsAdmin]

#     def get_queryset(self):
#         qs = Notes.objects.all()
#         subject_id = self.request.GET.get("subject_id")
#         if subject_id:
#             qs = qs.filter(subject_id=subject_id)
#         return qs

from rest_framework.parsers import MultiPartParser, FormParser

class AdminNotesListCreateAPIView(ListCreateAPIView):
    serializer_class = AdminNotesSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]

    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Notes.objects.all()
        subject_id = self.request.GET.get("subject_id")
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        return qs




class AdminNotesDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminNotesSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Notes.objects.all()




class AdminContactListAPIView(ListAPIView):
    serializer_class = AdminContactSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Contact.objects.all()




class AdminContactDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = AdminContactSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = Contact.objects.all()




class AdminUserListAPIView(ListAPIView):
    serializer_class = AdminUserListSerializer
    authentication_classes = []
    permission_classes = [IsAdmin]
    queryset = UserRegister.objects.all()




class AdminDashboardAPIView(GenericAPIView):
    authentication_classes = []
    permission_classes = [IsAdmin]
    def get(self, request):
        data = {
            "counts": {
                "departments": Department.objects.count(),
                "years": Year.objects.count(),
                "subjects": Subject.objects.count(),
                "notes": Notes.objects.count(),
                "users": UserRegister.objects.count(),
                "contacts": Contact.objects.count(),
                "comments": Comments.objects.count(),
                "ratings": Rating.objects.count(),
            },
            "recent_notes": NotesSerializer(Notes.objects.order_by("-upload_date")[:10], many=True).data,
            "recent_contacts": ContactSerializer(Contact.objects.order_by("-created_at")[:5], many=True).data,
        }
        return Response({"status": True, "data": data}, status=status.HTTP_200_OK)
    




class AdminLoginAPIView(GenericAPIView):
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        if verify_admin_credentials(username, password):
            refresh = RefreshToken()
            refresh["role"] = "admin"
            refresh["username"] = username
            return Response(
                {
                    "message": "Admin login successful.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)
                },status=status.HTTP_200_OK)
        return Response({"error": "Invalid username or password."},status=status.HTTP_401_UNAUTHORIZED)