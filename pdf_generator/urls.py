from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('creator.urls')),  # Include the urls from the pdf_service app
]
