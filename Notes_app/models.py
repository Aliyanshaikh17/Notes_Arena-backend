from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta


class UserRegister(AbstractUser):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile/", blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.full_name



    
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




class Year(models.Model):
    YEAR_CHOICES = (
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
    )
    year_number = models.CharField(max_length=20, choices=YEAR_CHOICES)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,related_name="years")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("year_number", "department")
    def __str__(self):
        return f"{self.department.name} - {self.year_number}"



    
class Subject(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to="subjects/")
    department = models.ForeignKey(Department,on_delete=models.CASCADE,related_name="subjects")
    year = models.ForeignKey(Year,on_delete=models.CASCADE,related_name="subjects")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "department", "year")
    def __str__(self):
        return self.name



    
class Notes(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE,related_name="notes")
    file = models.FileField(upload_to="notes/")
    uploaded_by = models.ForeignKey(UserRegister,on_delete=models.SET_NULL,null=True,blank=True)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    downloads = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title




class Comments(models.Model):
    user = models.ForeignKey(UserRegister,on_delete=models.CASCADE,related_name="comments")
    notes = models.ForeignKey(Notes,on_delete=models.CASCADE,related_name="comments")
    text = models.TextField()
    comment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-comment_date"]
    def __str__(self):
        return f"{self.user.full_name} - {self.notes.title}"




class Rating(models.Model):

    RATING_CHOICES = (
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    )
    user = models.ForeignKey(UserRegister,on_delete=models.CASCADE,related_name="ratings")
    notes = models.ForeignKey(Notes,on_delete=models.CASCADE,related_name="ratings")
    rating = models.IntegerField(choices=RATING_CHOICES)
    rating_text = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("user", "notes")
    def __str__(self):
        return f"{self.user.full_name} - {self.rating}"




class Contact(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    department = models.ForeignKey(Department,on_delete=models.SET_NULL,null=True,blank=True)
    year = models.ForeignKey(Year,on_delete=models.SET_NULL,null=True,blank=True)
    subject = models.ForeignKey(Subject,on_delete=models.SET_NULL,null=True,blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name





class OTPVerification(models.Model):
    user = models.ForeignKey(
        UserRegister,
        on_delete=models.CASCADE,
        related_name="otp_verifications"
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True,null=True)
    is_verified = models.BooleanField(default=False)
    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.expires_at is None:
            self.expires_at = timezone.now() + timedelta(minutes=5)

        super().save(*args, **kwargs)
    def is_expired(self):
        return timezone.now() > self.expires_at
    def __str__(self):
        return f"{self.user.email} - {self.otp}"