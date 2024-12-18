from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from django.urls import path
from .views import UploadTemplateView, ViewTemplateView, add_to_cart

urlpatterns = [
    path('upload/', UploadTemplateView.as_view(), name='upload_template'),
    path('view/<int:pk>/', ViewTemplateView.as_view(), name='view_template'),  # Match `pk`
    path('ckeditor/', include('ckeditor_uploader.urls')),  # Add this
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
