from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils import timezone

VERIFICATION_EXPIRY_HOURS = 24

# ---------------- USER MANAGER ----------------
class UserManager(BaseUserManager):

    def create_user(self, email, name, student_id, password=None):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=name,
            student_id=student_id
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, student_id, password):

        user = self.create_user(email, name, student_id, password)

        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True
        user.is_email_verified = True
        user.is_verified = True

        user.save(using=self._db)
        return user


# ---------------- USER MODEL ----------------
class User(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("second_admin", "2nd Admin"),
        ("advisor",      "Advisor"), 
        ("member", "Member"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=50, unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")

    # ---------------- EMAIL VERIFICATION ----------------
    is_email_verified = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    email_verification_token = models.UUIDField(
    default=uuid.uuid4,
    null=True,
    blank=True,
    unique=True
    )
    verification_token_created_at = models.DateTimeField(default=timezone.now)
    token_created_at = models.DateTimeField(null=True, blank=True)

    # ---------------- ADMIN VERIFICATION ----------------
    is_verified = models.BooleanField(default=False)

    # ---------------- STATUS ----------------
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    # ---------------- AUTH SETTINGS ----------------
    password_reset_token = models.UUIDField(null=True, blank=True, editable=False)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "student_id"]

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"

    # ---------------- HELPERS ----------------
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_second_admin(self):
        return self.role == "second_admin"
    
    @property
    def is_advisor(self):
        return self.role == 'advisor'

    @property
    def can_post(self):
        return self.role in ["admin", "second_admin"]
    
    @property
    def password_reset_expired(self):
        if not self.password_reset_token_created_at:
            return True
        from django.utils import timezone
        expiry = self.password_reset_token_created_at + timezone.timedelta(hours=2)
        return timezone.now() > expiry

    def generate_password_reset_token(self):
        import uuid
        from django.utils import timezone
        self.password_reset_token = uuid.uuid4()
        self.password_reset_token_created_at = timezone.now()
        self.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])

    @property
    def verification_expired(self):
        if self.is_email_verified:
            return False
        expiry = self.verification_token_created_at + \
                timezone.timedelta(hours=VERIFICATION_EXPIRY_HOURS)
        return timezone.now() > expiry

    def regenerate_verification_token(self):
        import uuid
        self.email_verification_token = uuid.uuid4()
        self.verification_token_created_at = timezone.now()
        self.save(update_fields=['email_verification_token',
                                'verification_token_created_at'])

    # ---------------- TOKEN CHECK ----------------
    def is_token_expired(self):
        return timezone.now() > self.token_created_at + timezone.timedelta(minutes=5)


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





