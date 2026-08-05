from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *
from .models import UserRegister, OTPVerification
from .utils import generate_otp, send_otp_email
from django.utils import timezone
from .models import Comments
from django.contrib.auth import authenticate

import re
from django.contrib.auth.password_validation import validate_password




class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = UserRegister
        fields = [

            "full_name",
            "username",
            "email",
            "password",
            "confirm_password",
            "phone_number"

        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:

            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        return UserRegister.objects.create(**validated_data)






class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid Email or Password.")
        attrs["user"] = user
        return attrs




class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not UserRegister.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate_otp(self, value):
        if not re.fullmatch(r"\d{6}", value):
            raise serializers.ValidationError("OTP must be exactly 6 digits.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value




class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegister
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "phone_number",
            "profile_image",
        ]




class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"




class YearSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    class Meta:
        model = Year
        fields = [
            "id",
            "year_number",
            "department"
        ]




class SubjectSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source="department.name", read_only=True)
    year = serializers.CharField(source="year.year_number", read_only=True)
    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "description",
            "image",
            "department",
            "year",
            "created_at"
        ]








class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "id",
            "department",
            "year",
            "name",
            "description",
            "created_at",
        ]




class NotesSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    file = serializers.SerializerMethodField()

    class Meta:
        model = Notes
        fields = [
            "id",
            "subject",
            "subject_name",
            "title",
            "description",
            "file",
            "upload_date",
            "downloads",
            "is_active",
        ]

    def get_file(self, obj):
        request = self.context.get("request")
        if obj.file:
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None




class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    class Meta:
        model = Comments
        fields = [
            "id",
            "notes",
            "user",
            "user_name",
            "text",
            "comment_date",
        ]
        read_only_fields = [
            "user",
            "comment_date",
        ]



class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            "id",
            "notes",
            "user",
            "rating",
            "rating_text",
            "date",
        ]
        read_only_fields = [
            "user",
            "date",
        ]


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "department",
            "year",
            "subject",
            "message",
            "created_at",
        ]
        read_only_fields = ["created_at"]






class AdminDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"





class AdminYearSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    class Meta:
        model = Year
        fields = [
            "id",
            "department",
            "department_name",
            "year_number",
        ]




class AdminSubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    year_number = serializers.CharField(source="year.year_number", read_only=True)
    class Meta:
        model = Subject
        fields = [
            "id",
            "department",
            "department_name",
            "year",
            "year_number",
            "name",
            "description",
            "created_at",
        ]





class AdminNotesSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    class Meta:
        model = Notes
        fields = [
            "id",
            "subject",
            "subject_name",
            "title",
            "description",
            "file",
            "upload_date",
            "downloads",
            "is_active",
        ]
        read_only_fields = [
            "upload_date",
            "downloads",
        ]




class AdminContactSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name",
        read_only=True)
    year_number = serializers.CharField(
        source="year.year_number",
        read_only=True)

    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "department",
            "department_name",
            "year",
            "year_number",
            "subject",
            "subject_name",
            "message",
            "created_at",
        ]




class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegister
        fields = [
            "id",
            "full_name",
            "username",
            "email",
            "phone_number",
            "is_staff",
            "is_active",
            "date_joined",
        ]




class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)