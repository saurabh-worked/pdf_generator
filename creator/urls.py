from django.urls import path
from creator import views

urlpatterns = [
    path('generate-pdf/', views.post_pdf, name='generate_pdf'),
]
