from django.urls import path
from .views import (
    home_page, add_student, get_students, edit_students, delete_students,
    delete_user, register_students, login_student, logout_student,
    get_user, add_school, get_school
)

urlpatterns = [
    path("", home_page, name="home"),
    path("add/", add_student, name="add"),
    path("students/", get_students, name='students'),
    path("school/", get_school, name='school'),
    path("user/", get_user, name='user'),
    path("edit/<int:id>/", edit_students, name='edit_students'),
    path("students/delete/<int:id>/", delete_students, name='delete_students'),
    path("users/delete/<int:id>/", delete_user, name='delete_user'),
    path("register/", register_students, name='register'),
    path("login/", login_student, name='login'),
    path("logout/", logout_student, name='logout'),
    path("add_school/", add_school, name="add_school"),
]
