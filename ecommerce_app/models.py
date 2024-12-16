from django.db import models
from django.contrib.auth.models import User

from ckeditor.fields import RichTextField

class UserTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    html_content = RichTextField()  # Use CKEditor for rich-text editing
    css_content = models.TextField()
    js_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Template by {self.user.username} on {self.created_at}"

