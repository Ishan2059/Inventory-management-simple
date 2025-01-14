from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Profile(models.Model):
    staff=models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200)
    phone = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be 10 digits."
            )
        ],
        null=True,
        blank=True
    )
    images = models.ImageField(default='avatar.jpg', upload_to='Profile_Images')

    def __str__(self):
        return f"{self.staff.username}-Profile"