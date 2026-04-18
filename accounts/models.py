from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, name, student_id, password=None):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, student_id=student_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, student_id, password):
        user = self.create_user(email, name, student_id, password)
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.is_email_verified = True
        user.is_verified = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('second_admin', '2nd Admin'),
        ('member', 'Member'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # verified by 2nd admin/admin
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'student_id']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_second_admin(self):
        return self.role == 'second_admin'

    @property
    def can_post(self):
        return self.role in ['admin', 'second_admin']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    batch = models.CharField(max_length=50, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    pending_verification = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.name}"


class PreAdmin(models.Model):
    """Pre-defined 2nd admins - matched on signup/profile update"""
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.designation}"
