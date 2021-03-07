from django.urls import path
from .views import StudentView, TeacherView

urlpatterns = [
    path("students", StudentView.as_view(), name="students",),
    path("teachers", TeacherView.as_view(), name="teachers",),
]
