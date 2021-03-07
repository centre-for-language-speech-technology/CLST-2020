from django.views.generic import TemplateView


class StudentView(TemplateView):
    """Student Explainer view."""

    template_name = "explainer/students.html"


class TeacherView(TemplateView):
    """Teacher Explainer view."""

    template_name = "explainer/teacher.html"
