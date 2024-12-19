from django.db import models
from django.contrib.auth.models import User

from ckeditor.fields import RichTextField

class UserTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    html_content = RichTextField()  # Use CKEditor for rich-text editing
    css_content = models.TextField()
    js_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image_dir = models.CharField(max_length=255, blank=True, null=True)  # New field to store image directory

    def __str__(self):
        return f"Template by {self.user.username} on {self.created_at}"

from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
